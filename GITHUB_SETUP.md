# Instruções para Criar Repositório no GitHub

## Passo a Passo

### 1. Criar Repositório no GitHub

1. Acesse [GitHub](https://github.com)
2. Clique no botão **"+"** no canto superior direito
3. Selecione **"New repository"**
4. Preencha os dados:
   - **Repository name**: `backend-vr-forge` (ou `Backend-VR-Forge`)
   - **Description**: "Plataforma enterprise para forjar, gerenciar e treinar modelos de IA proprietários VR"
   - **Visibility**: Escolha **Private** ou **Public**
   - **NÃO** marque "Initialize this repository with a README" (já temos um)
   - **NÃO** adicione .gitignore ou license (já temos)
5. Clique em **"Create repository"**

### 2. Conectar e Fazer Push

Após criar o repositório, o GitHub mostrará instruções. Execute os comandos abaixo no terminal:

```bash
cd "/home/alex/Documentos/Backend VR Forge"

# Adicionar remote (substitua SEU_USUARIO pelo seu username do GitHub)
git remote add origin https://github.com/SEU_USUARIO/backend-vr-forge.git

# Ou se preferir SSH:
# git remote add origin git@github.com:SEU_USUARIO/backend-vr-forge.git

# Verificar remote adicionado
git remote -v

# Fazer push do código
git push -u origin main
```

### 3. Verificar no GitHub

Após o push, acesse seu repositório no GitHub e verifique:
- ✅ Todos os arquivos foram enviados
- ✅ README.md está visível
- ✅ Estrutura de pastas está correta

## Comandos Úteis

```bash
# Ver status do repositório
git status

# Ver histórico de commits
git log --oneline

# Ver branches
git branch

# Ver remotes configurados
git remote -v

# Fazer push de novas mudanças (após commits)
git push origin main

# Pull de mudanças remotas
git pull origin main
```

## Próximos Passos Após Push

1. **Configurar Secrets no GitHub** (se usar GitHub Actions):
   - Vá em Settings → Secrets and variables → Actions
   - Adicione variáveis de ambiente necessárias

2. **Configurar EasyPanel**:
   - Conecte o repositório GitHub
   - Configure variáveis de ambiente
   - O build automático será executado

3. **Adicionar Badges** (opcional):
   - Status do build
   - Coverage de testes
   - Versão do Python

## Troubleshooting

### Erro: "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/SEU_USUARIO/backend-vr-forge.git
```

### Erro: "failed to push some refs"
```bash
# Se o repositório GitHub foi criado com README, faça pull primeiro:
git pull origin main --allow-unrelated-histories
git push -u origin main
```

### Mudar URL do remote
```bash
git remote set-url origin https://github.com/SEU_USUARIO/backend-vr-forge.git
```

