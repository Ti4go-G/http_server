import json
from urllib.parse import unquote_plus
from utils import carregar_estoque, salvar_estoque, gerar_pagina_estoque


def build_response(status_code, content_type, body):
    return (
        f"HTTP/1.1 {status_code} OK\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(body)}\r\n"
        "\r\n"
    ).encode('utf-8') + body


def handle_get(route: bytes):
    if route == b'/estoque':
        html = gerar_pagina_estoque()
        return build_response(200, 'text/html', html.encode('utf-8'))

    elif route == b'/':
        # Redireciona para /estoque
        return b"HTTP/1.1 302 Found\r\nLocation: /estoque\r\n\r\n"

    elif route == b'/adicionar':
        try:
            with open('./new_prod.html', 'r', encoding='utf-8') as f:
                html = f.read()
            return build_response(200, 'text/html', html.encode('utf-8'))
        except FileNotFoundError:
            return build_response(404, 'text/html', b"<h1>404 - Pagina nao encontrada</h1>")


    #ROTA REST: /api/estoque
    elif route == b'/api/estoque':
        estoque = carregar_estoque()
        json_data = json.dumps(estoque, ensure_ascii=False, indent=2)
        return build_response(200, 'application/json', json_data.encode('utf-8'))

    else:
        return build_response(404, 'text/html', b"<h1>404 - Pagina nao encontrada</h1>")


def handle_post(route: bytes, data: bytes):
    if route == b'/salvar_produto':
        corpo = data.split(b'\r\n\r\n')[1].decode('utf-8')
        dados = {}
        for par in corpo.split('&'):
            chave, valor = par.split('=')
            dados[chave] = unquote_plus(valor)

        estoque = carregar_estoque()
        novo_id = estoque[-1]['id'] + 1 if estoque else 1

        novo_produto = {
            'id': novo_id,
            'nome': dados['nome'],
            'quantidade': int(dados['quantidade']),
            'preco': float(dados['preco'].replace(',', '.')),
            'data_validade': dados['validade']
        }

        estoque.append(novo_produto)
        salvar_estoque(estoque)

        # Redireciona para /estoque
        return b"HTTP/1.1 302 Found\r\nLocation: /estoque\r\n\r\n"

    else:
        return build_response(404, 'text/html', b"<h1>404 - Rota POST nao encontrada</h1>")
