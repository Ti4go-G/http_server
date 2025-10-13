import json
from urllib.parse import unquote_plus

# --- Persistência ---
def carregar_estoque():
    try:
        with open('estoque.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("[ERRO] Não foi possível carregar o estoque.")
        return []

def salvar_estoque(estoque):
    with open('estoque.json', 'w', encoding='utf-8') as f:
        json.dump(estoque, f, indent=2, ensure_ascii=False)

# --- Página HTML do estoque ---
def gerar_pagina_estoque():
    estoque = carregar_estoque()
    linhas_tabela = ""

    if not estoque:
        linhas_tabela = '<tr><td colspan="4">Nenhum produto cadastrado.</td></tr>'
    else:
        for p in estoque:
            linhas_tabela += f"""
            <tr>
                <td>{p['id']}</td>
                <td>{p['nome']}</td>
                <td>{p['quantidade']}</td>
                <td>R$ {p['preco']:.2f}</td>
            </tr>
            """

    return f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>Controle de Estoque</title>
        <style>
            body {{ font-family: sans-serif; margin: 2em; }}
            table {{ border-collapse: collapse; width: 80%; margin-top: 1em; }}
            th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            a {{ text-decoration: none; background: #007bff; color: white; padding: 8px 12px; border-radius: 4px; }}
        </style>
    </head>
    <body>
        <h1>Controle de Estoque</h1>
        <a href="/adicionar">Adicionar Produto</a>
        <table>
            <thead>
                <tr>
                    <th>ID</th><th>Nome</th><th>Quantidade</th><th>Preço</th>
                </tr>
            </thead>
            <tbody>{linhas_tabela}</tbody>
        </table>
    </body>
    </html>
    """

# --- Parse de formulário (POST) ---
def parse_form_data(data):
    corpo = data.split(b'\r\n\r\n')[1].decode('utf-8')
    dados = {}
    for par in corpo.split('&'):
        chave, valor = par.split('=')
        dados[chave] = unquote_plus(valor)
    return dados

# --- Logs de requisição ---
def log_request(addr, method, route):
    print(f"[REQ] {addr[0]}:{addr[1]} -> {method} {route}")
