import socket
import json
from urllib.parse import unquote_plus 

def carregar_estoque():
    try:
        with open('estoque.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("Erro ao carregar o estoque.")
        return []

def salvar_estoque(estoque):

    with open('estoque.json', 'w', encoding='utf-8') as f:
        json.dump(estoque, f, indent=2, ensure_ascii=False)

def gerar_pagina_estoque():

    estoque = carregar_estoque()
    
    linhas_tabela = ""
    if not estoque:
        linhas_tabela = '<tr><td colspan="4">Nenhum produto no estoque.</td></tr>'
    else:
        for produto in estoque:
            linhas_tabela += f"""
            <tr>
                <td>{produto['id']}</td>
                <td>{produto['nome']}</td>
                <td>{produto['quantidade']}</td>
                <td>R$ {produto['preco']:.2f}</td>
            </tr>
            """

    # Template HTML da página
    html = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>Controle de Estoque</title>
        <style>
            body {{ font-family: sans-serif; }}
            table {{ width: 80%; border-collapse: collapse; margin-top: 1em; }}
            th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            a {{ text-decoration: none; background-color: #007bff; color: white; padding: 10px 15px; border-radius: 5px;}}
        </style>
    </head>
    <body>
        <h1>Controle de Estoque</h1>
        <a href="/adicionar">Adicionar Novo Produto</a>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Nome do Produto</th>
                    <th>Quantidade</th>
                    <th>Preço Unitário</th>
                </tr>
            </thead>
            <tbody>
                {linhas_tabela}
            </tbody>
        </table>
    </body>
    </html>
    """
    return html

# --- Configuração do Servidor ---
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 8080))
s.listen(5)
print("Servidor de Estoque escutando na porta 8080...")

try:
    while True:
        ws, addr = s.accept()
        data = ws.recv(4096)
        if not data:
            continue

        request_line = data.split(b'\r\n')[0]
        try:
            method, route, _ = request_line.split(b' ')
        except ValueError:
            ws.close()
            continue

        # --- Roteamento ---

        if method == b'GET' and route == b'/estoque':
            pagina_html = gerar_pagina_estoque()
            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {len(pagina_html)}\r\n\r\n{pagina_html}"
            ws.sendall(response.encode('utf-8'))

        elif method == b'GET' and route == b'/adicionar':
            try:
                with open('templates/new_prod.html', 'r', encoding='utf-8') as f:
                    form_html = f.read()
                response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {len(form_html)}\r\n\r\n{form_html}"
                ws.sendall(response.encode('utf-8'))
            except FileNotFoundError:
                response = "HTTP/1.1 404 Not Found\r\n\r\n<h1>Página não encontrada</h1>"
                ws.sendall(response.encode('utf-8'))

        elif method == b'POST' and route == b'/salvar_produto':
            # Extrair o corpo da requisição
            corpo = data.split(b'\r\n\r\n')[1].decode('utf-8')
            
            # Parse dos dados do formulário (ex: nome=Mouse&quantidade=10&preco=79.90)
            dados = {}
            for par in corpo.split('&'):
                chave, valor = par.split('=')
                # unquote_plus decodifica caracteres especiais como '+' para espaço
                dados[chave] = unquote_plus(valor)

            estoque = carregar_estoque()
            
            novo_id = estoque[-1]['id'] + 1 if estoque else 1
            novo_produto = {
                'id': novo_id,
                'nome': dados['nome'],
                'quantidade': int(dados['quantidade']),
                'preco': float(dados['preco'].replace(',', '.'))
            }

            estoque.append(novo_produto)
            salvar_estoque(estoque)

            # O código 302 informa ao browser para fazer uma nova requisição GET para o 'Location'
            response = "HTTP/1.1 302 Found\r\nLocation: /estoque\r\n\r\n"
            ws.sendall(response.encode('utf-8'))

        else:
            # Rota padrão: redireciona para o estoque ou mostra 404
            if route == b'/':
                response = "HTTP/1.1 302 Found\r\nLocation: /estoque\r\n\r\n"
            else:
                response = "HTTP/1.1 404 Not Found\r\n\r\n<h1>404 Rota não encontrada</h1>"
            ws.sendall(response.encode('utf-8'))
        
        ws.close()

except KeyboardInterrupt:
    print("\nServidor terminado.")
finally:
    s.close()