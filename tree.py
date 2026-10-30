import os

IGNORAR = {
    '__pycache__', '.git', '.idea', '.vscode', 'node_modules',
    'venv', '.venv', 'env', 'staticfiles', 'media', 'dist', 'build',
    '.pytest_cache', '.mypy_cache', '.DS_Store', 'db.sqlite3'
}
IGNORAR_EXT = {'.pyc', '.pyo', '.log', '.sqlite3'}

def estrutura(caminho, prefixo=""):
    try:
        itens = sorted(os.listdir(caminho))
    except PermissionError:
        return
    itens = [i for i in itens
             if i not in IGNORAR
             and not any(i.endswith(e) for e in IGNORAR_EXT)]
    for idx, item in enumerate(itens):
        caminho_item = os.path.join(caminho, item)
        ultimo = idx == len(itens) - 1
        print(f"{prefixo}{'└── ' if ultimo else '├── '}{item}")
        if os.path.isdir(caminho_item):
            estrutura(caminho_item, prefixo + ("    " if ultimo else "│   "))

raiz = os.getcwd()
print(f"\n📁 {os.path.basename(raiz)}/\n")
estrutura(raiz)
