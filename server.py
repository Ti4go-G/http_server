import socket
from routes import handle_get, handle_post

HOST = ''
PORT = 8080

def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(5)
    print(f"Servidor HTTP ativo em http://localhost:{PORT}")

    try:
        while True:
            conn, addr = s.accept()
            data = conn.recv(8192)

            if not data:
                conn.close()
                continue

            # --- Exibir o cabeçalho completo da requisição ---
            print("\n===================== NOVA REQUISIÇÃO =====================")
            try:
                print(data.decode('utf-8'))
            except UnicodeDecodeError:
                print("(conteúdo binário recebido)")

            request_line = data.split(b'\r\n')[0]
            try:
                method, route, _ = request_line.split(b' ')
            except ValueError:
                conn.close()
                continue

            # --- Roteamento básico ---
            if method == b'GET':
                response = handle_get(route)
            elif method == b'POST':
                response = handle_post(route, data)
            else:
                response = b"HTTP/1.1 405 Method Not Allowed\r\n\r\nMetodo nao suportado."

            conn.sendall(response)
            conn.close()

    except KeyboardInterrupt:
        print("\nServidor encerrado.")
    finally:
        s.close()

if __name__ == "__main__":
    start_server()
