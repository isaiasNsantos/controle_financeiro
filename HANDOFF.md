
---

### 2. `HANDOFF.md` (O guia de Deploy para o futuro)
Crie este arquivo para documentar exatamente o que fizemos e o que falta fazer quando você for subir para o PythonAnywhere (ou qualquer outro servidor).

```markdown
# 📋 Handoff: Guia de Deploy (PythonAnywhere)

Este documento serve como um checklist para colocar a aplicação em produção no PythonAnywhere.

## 🛠️ Configurações já realizadas no projeto:
- [x] `SECRET_KEY` isolada no arquivo `.env`.
- [x] `DEBUG` configurado via variável de ambiente.
- [x] `ALLOWED_HOSTS` preparado para ler do `.env`.
- [x] `STATIC_ROOT` configurado (`BASE_DIR / 'staticfiles'`).
- [x] Banco de dados SQLite configurado.
- [x] Arquivo `.gitignore` protegendo o `venv`, `db.sqlite3` e `.env`.

## 🚀 Passo a passo para o Deploy no PythonAnywhere:

### 1. Preparação da Conta
- Conta criada: `isaiasns.pythonanywhere.com`
- Lembrar de clicar em **"Run until 1 month from today"** todo mês para o site não dormir.

### 2. Clonando o projeto e criando o ambiente
No console (Bash) do PythonAnywhere:
```bash
# Clonar o repositório
git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git

# Entrar na pasta
cd SEU_REPOSITORIO

# Criar o ambiente virtual (usando a versão do Python instalada)
mkvirtualenv --python=/usr/bin/python3.10 venv_financas

# Instalar dependências
pip install -r requirements.txt