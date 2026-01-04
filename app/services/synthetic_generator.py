"""Synthetic dataset generator service."""

import json
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.integrations.llm_providers.factory import get_provider
from app.models.dataset import Dataset
from app.models.dataset_item import DatasetItem
from app.models.generation_template import GenerationTemplate
from app.models.segment import Segment
from app.services.quality_engine import QualityEngine

logger = get_logger(__name__)


class SyntheticGeneratorService:
    """Service for generating synthetic dataset items."""

    @staticmethod
    async def generate_items(
        db: AsyncSession,
        dataset_id: str,
        segment_ids: Optional[list[str]] = None,
        max_items: Optional[int] = None,
        batch_size: int = 10,
    ) -> list[DatasetItem]:
        """Generate synthetic dataset items.

        Args:
            db: Database session
            dataset_id: Dataset ID
            segment_ids: Specific segment IDs to use (optional)
            max_items: Maximum items to generate
            batch_size: Batch size for generation

        Returns:
            List of generated dataset items

        Raises:
            NotFoundError: If dataset or segments not found
        """
        # Get dataset
        result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
        dataset = result.scalar_one_or_none()
        if not dataset:
            raise NotFoundError("Dataset", dataset_id)

        # Get template if available
        template = None
        if dataset.template_id:
            result = await db.execute(
                select(GenerationTemplate).where(GenerationTemplate.id == dataset.template_id)
            )
            template = result.scalar_one_or_none()

        # Get segments
        if segment_ids:
            segments = []
            for seg_id in segment_ids:
                result = await db.execute(select(Segment).where(Segment.id == seg_id))
                segment = result.scalar_one_or_none()
                if not segment:
                    raise NotFoundError("Segment", seg_id)
                segments.append(segment)
        else:
            # Use segment filter from dataset
            query = select(Segment).where(Segment.domain_id == dataset.domain_id)
            if dataset.use_case:
                query = query.where(Segment.use_case == dataset.use_case)
            if dataset.segment_filter.get("segment_type"):
                query = query.where(
                    Segment.segment_type == dataset.segment_filter["segment_type"]
                )

            result = await db.execute(query)
            segments = list(result.scalars().all())

        if max_items:
            segments = segments[:max_items]

        # Get LLM provider
        provider = get_provider(dataset.provider)

        # Prepare prompts
        system_prompt = (
            template.system_prompt
            if template
            else "You are an expert at creating high-quality training examples for AI models."
        )
        user_template = (
            template.user_prompt_template
            if template
            else "Create a training example based on this content:\n\n{content}\n\nGenerate an instruction, input (if needed), ideal response, bad response, and explanation."
        )

        # Generate items
        generated_items = []
        for i in range(0, len(segments), batch_size):
            batch = segments[i : i + batch_size]
            for segment in batch:
                try:
                    # Format user prompt
                    user_prompt = user_template.format(content=segment.content)

                    # Generate with LLM
                    response = await provider.generate_json(
                        system_prompt=system_prompt,
                        user_prompt=user_prompt,
                        model=dataset.target_model_family or "gpt-4-turbo-preview",
                    )

                    # Extract fields
                    instruction = response.get("instruction", "")
                    input_text = response.get("input", "")
                    ideal_response = response.get("ideal_response", "")
                    bad_response = response.get("bad_response", "")
                    explanation = response.get("explanation", "")

                    # Validate quality
                    quality_score, quality_flags = QualityEngine.validate_item(
                        instruction=instruction,
                        ideal_response=ideal_response,
                        input_text=input_text,
                    )

                    # Create dataset item
                    item = DatasetItem(
                        dataset_id=dataset_id,
                        segment_id=segment.id,
                        source_provider=dataset.provider,
                        instruction=instruction,
                        input_text=input_text if input_text else None,
                        ideal_response=ideal_response,
                        bad_response=bad_response if bad_response else None,
                        explanation=explanation if explanation else None,
                        status="pending_review",
                        quality_score=quality_score,
                        quality_flags=quality_flags,
                        meta_data={},
                    )

                    db.add(item)
                    generated_items.append(item)

                except Exception as e:
                    logger.error(
                        "Failed to generate item for segment",
                        segment_id=segment.id,
                        error=str(e),
                    )
                    continue

            await db.commit()

        # Update dataset stats
        dataset.total_items = len(generated_items)
        dataset.pending_items = len(generated_items)
        dataset.status = "ready"
        await db.commit()

        for item in generated_items:
            await db.refresh(item)

        logger.info(
            "Dataset items generated",
            dataset_id=dataset_id,
            count=len(generated_items),
        )

        return generated_items

