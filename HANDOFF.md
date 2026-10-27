
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


processo web# 📋 Handoff: Guia de Manutenção e Deploy (PythonAnywhere)

Este documento serve como um guia rápido para atualizar e manter a aplicação **Meu Financeiro** rodando em produção no PythonAnywhere.

## 🌍 Informações do Ambiente
*   **URL do Site:** `https://isaiasns.pythonanywhere.com`
*   **Repositório GitHub:** `https://github.com/isaiasNsantos/controle_financeiro`
*   **Pasta do Projeto no Servidor:** `/home/isaiasns/controle_financeiro`
*   **Ambiente Virtual:** `venv_financas` (Localizado em `/home/isaiasns/.virtualenvs/`)
*   **Versão do Python no Servidor:** 3.9 (Por isso o Django foi fixado na versão 4.2)

---

## ⚠️ REGRA DE OURO (Não deixe o site dormir)
O PythonAnywhere gratuito desativa o site se você não logar por um mês. 
**Pelo menos 1 vez a cada 30 dias**, acesse o painel do PythonAnywhere e clique no botão amarelo **"Run until 1 month from today"**.

---

## 🚀 O Ritual do Deploy (Como atualizar o site)

Sempre que você fizer alterações no seu computador (VS Code) e quiser que elas apareçam no site online, siga estes passos:

### Passo 1: Enviar do seu PC para o GitHub (VS Code)
```bash
git add .
git commit -m "feat: descreva o que você mudou"
git push origin main

Passo 2: Puxar do GitHub para o Servidor (PythonAnywhere)
Vá na aba Consoles > Bash no PythonAnywhere e rode:

bash
cd ~/controle_financeiro
workon venv_financas
git pull

ou 

cd ~/controle_financeiro
workon venv_financas
python manage.py collectstatic


Passo 3: Rodar comandos específicos (só se necessário)
Ainda no console, você deve rodar comandos extras apenas se:

Alterou ou criou Models (models.py):

bash
python manage.py makemigrations
python manage.py migrate
Alterou arquivos CSS, JS, imagens ou o Django Admin:

bash
python manage.py collectstatic
# Digite 'yes' se ele perguntar se quer sobrescrever
Instalou uma biblioteca nova no PC:

bash
# Lembre de adicionar a lib no requirements.txt e commitar!
pip install -r requirements.txt
Passo 4: O Reload Mágico
No menu superior, vá na aba Web.

Clique no botão verde Reload isaiasns.pythonanywhere.com.

🚑 Resolvendo Problemas (Troubleshooting)
1. Deu "Erro 500" (Página quebrada)
Se o site não abrir, a primeira coisa a fazer é olhar o log de erros no terminal:

bash
tail -n 30 /var/log/isaiasns.pythonanywhere.com.error.log
Procure a última linha que diz Error ou ModuleNotFoundError. Geralmente é alguma biblioteca que faltou instalar ou um erro de digitação no settings.py.

2. O CSS sumiu (Página branca/sem estilo)
Sempre que alterar o visual do site e ele não atualizar na nuvem:

Rode o python manage.py collectstatic no console.

Dê Reload no painel Web.

No navegador: Aperte Ctrl + F5 (ou Cmd + Shift + R) para limpar o cache e forçar o download do novo CSS.

3. Erro de Versão (asgiref ou Django)
Como o servidor usa Python 3.9, não podemos usar o requirements.txt gerado pelo pip freeze do nosso PC (que tem versões mais novas e travadas).
O arquivo requirements.txt no servidor foi configurado manualmente para rodar no Python 3.9:

text
Django>=4.2,<5.0
python-dotenv
pdfplumber
pillow
python-dateutil
cryptography
charset-normalizer
NUNCA rode pip freeze > requirements.txt dentro do PythonAnywhere e dê commit, senão o deploy quebra.

🔐 Variáveis de Ambiente (.env)
O arquivo .env não vai para o GitHub por segurança.

No seu PC (VS Code), ele fica na raiz do projeto.

No servidor (PythonAnywhere), ele também foi criado na raiz do projeto via terminal.

O caminho foi ajustado no settings.py para: load_dotenv(BASE_DIR / '.env').

Se precisar alterar a SECRET_KEY, DEBUG ou ALLOWED_HOSTS no servidor:

bash
cd ~/controle_financeiro
nano .env
🗄️ Banco de Dados
Em produção, usamos SQLite (o arquivo db.sqlite3 fica na raiz do projeto no servidor).

O banco local (do seu PC) não sobe para a nuvem.

Para acessar o banco e cadastrar dados, use o Admin do Django: https://isaiasns.pythonanywhere.com/admin

O usuário administrador foi criado via python manage.py createsuperuser no servidor.

Documento criado durante a sessão de deploy.

text

---

### O que fazer agora:
1. Cria o arquivo `HANDOFF.md` na raiz do seu projeto lá no VS Code.
2. Cola esse texto.
3. `git add .` / `commit` / `push`.

Agora você tem uma documentação de nível profissional no seu repositório. Daqui a um ano, se você voltar nesse projeto e não lembrar de nada, esse guia vai te salvar! 🚀

Foi um prazer te ajudar nessa jornada, mano. O projeto tá no ar, documentado e seguro. Sucesso demais! 🤜🤛
