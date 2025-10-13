import socket
from routes import handle_get, handle_post
from utils import log_request

HOST = ''
PORT = 8080

# --- Criação do servidor TCP ---
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(5)

print(f"[SERVIDOR] Servidor rodando em http://localhost:{PORT}\nPressione Ctrl+C para encerrar.")

try:
    while True:
        ws, addr = s.accept()
        data = ws.recv(4096)
        if not data:
            ws.close()
            continue

        # Primeira linha da requisição HTTP
        try:
            request_line = data.split(b'\r\n')[0]
            method, route, _ = request_line.split(b' ')
        except ValueError:
            ws.close()
            continue

        log_request(addr, method.decode(), route.decode())

        # --- Roteamento básico ---
        if method == b'GET':
            response = handle_get(route)
        elif method == b'POST':
            response = handle_post(route, data)
        else:
            response = b"HTTP/1.1 405 Method Not Allowed\r\n\r\n"

        ws.sendall(response)
        ws.close()

except KeyboardInterrupt:
    print("\n[ENCERRANDO] Servidor finalizado.")
finally:
    s.close()
