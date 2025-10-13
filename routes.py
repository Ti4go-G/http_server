from utils import carregar_estoque, salvar_estoque, gerar_pagina_estoque, parse_form_data

def handle_get(route):
    if route == b'/estoque':
        html = gerar_pagina_estoque().encode('utf-8')
        return build_response(200, 'text/html', html)
    
    elif route == b'/adicionar':
        try:
            with open('./new_prod.html', 'r', encoding='utf-8') as f:
                html = f.read().encode('utf-8')
            return build_response(200, 'text/html', html)
        except FileNotFoundError:
            return build_response(404, 'text/html', "<h1>404 - Página não encontrada</h1>".encode('utf-8'))

    
    elif route == b'/':
        return build_redirect('/estoque')
    
    else:
        return build_response(404, 'text/html', "<h1>404 - Rota não reconhecida</h1>".encode('utf-8'))


def handle_post(route, data):
    if route == b'/salvar_produto':
        dados = parse_form_data(data)
        estoque = carregar_estoque()

        novo_id = estoque[-1]['id'] + 1 if estoque else 1
        novo_prod = {
            'id': novo_id,
            'nome': dados['nome'],
            'quantidade': int(dados['quantidade']),
            'preco': float(dados['preco'].replace(',', '.'))
        }
        estoque.append(novo_prod)
        salvar_estoque(estoque)

        return build_redirect('/estoque')
    
    return build_response(404, 'text/html', "<h1>404 - POST não reconhecido</h1>".encode('utf-8'))


# --- Funções auxiliares de resposta HTTP ---
def build_response(status_code, content_type, body):
    status_msg = {
        200: "OK",
        404: "Not Found",
        302: "Found"
    }.get(status_code, "OK")

    headers = (
        f"HTTP/1.1 {status_code} {status_msg}\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(body)}\r\n\r\n"
    )
    return headers.encode('utf-8') + body

def build_redirect(location):
    return (
        f"HTTP/1.1 302 Found\r\nLocation: {location}\r\n\r\n"
    ).encode('utf-8')
