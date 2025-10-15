import json
from urllib.parse import unquote_plus
from datetime import date, timedelta

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
    hoje = date.today()
    linhas_tabela = ""

    if not estoque:
        linhas_tabela = '<tr><td colspan="4">Nenhum produto cadastrado.</td></tr>'
    else:
        for p in estoque:
            validade_str = p.get('data_validade', '1900-01-01') # Pega a data ou um valor padrão antigo
            validade_obj = date.fromisoformat(validade_str)
            dias_restantes = (validade_obj - hoje).days
            
            classe_css = "ok" 
            if dias_restantes < 0:
                classe_css = "vencido"
            elif dias_restantes <= 30: # produtos vencendo em 30 dias ou menos
                classe_css = "alerta"
            

            validade_formatada = validade_obj.strftime('%d/%m/%Y')
            if dias_restantes < 0:      
                validade_info = 'Vencido'
            else:
                validade_info = f'{dias_restantes} dias'
            linhas_tabela += f"""
            <tr class="{classe_css}">
                <td>{p['id']}</td>
                <td>{p['nome']}</td>
                <td>{p['quantidade']}</td>
                <td>R$ {p.get('preco', 0):.2f}</td>
                <td>{validade_formatada} ({validade_info})</td>
            </tr>
            """

    return f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>Controle de Estoque</title>
        <style>
            body {{
                font-family: sans-serif;
                margin: 0;
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                background-image: linear-gradient(to bottom right, #007bff, #4e00b3);
            }}
            .card {{
                background: rgba(249, 249, 249, 0.6);
                padding: 24px;
                border-radius: 10px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.18);
                max-width: 900px;
                width: 95%;
                display: flex;
                flex-direction: column;
                gap: 16px;
                align-items: center;
            }}
            h1 {{ margin: 0 0 8px 0; }}
            .actions {{ display: flex; gap: 12px; justify-content: flex-end; margin-bottom: 12px; width: 100%; }}
            .btn {{ text-decoration: none; background: #007bff; color: white; padding: 8px 12px; border-radius: 6px; }}
            .btn:hover {{ background: #0056b3; }}
            table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 6px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }}
            thead th {{ text-align: left; padding: 12px 16px; background: linear-gradient(180deg,#f7f7f7,#efefef); color: #333; font-weight: 600; border-bottom: 1px solid #e6e6e6; }}
            tbody td {{ padding: 12px 16px; border-bottom: 1px solid #f1f1f1; }}
            tbody tr:hover td {{ background: #f3f7ff; }}
            tbody tr.vencido td {{ background-color: #ff4d4d !important; color: #fff; }}
            tbody tr.alerta td {{ background-color: #ffe066 !important; color: #222; }}
            tbody tr.ok td {{ background-color: #51cf66 !important; color: #fff; }}
            @media (max-width: 720px) {{
                .card {{ padding: 8px; }}
                table, thead, tbody, tr, td, th {{ display: block; width: 100%; }}
                thead {{ display: none; }}
                tbody tr {{ margin-bottom: 12px; border-radius: 6px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }}
                tbody td {{ padding: 10px 12px; display: flex; justify-content: space-between; border-bottom: none; }}
                tbody td::before {{ content: attr(data-label); color: #555; font-weight: 600; margin-right: 8px; }}
            }}
            .header {{ width: 100%; display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }}
        </style>
    </head>
    <body>
      <div class="card">
        <div class="header">
          <h1>Controle de Estoque</h1>
          <a class="btn" href="/adicionar">Adicionar Produto</a>
        </div>
        <table>
          <thead>
            <tr>
              <th>ID</th><th>Nome</th><th>Quantidade</th><th>Preço</th>
              <th>Validade (Dias Restantes)</th>
            </tr>
          </thead>
          <tbody>{linhas_tabela}</tbody>
        </table>
      </div>
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
