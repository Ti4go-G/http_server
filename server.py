import socket
from routes import handle_get, handle_post

HOST = '0.0.0.0'
PORT = 8080


def start_server():
    # --- Descobrir IPv4 da rede ---
    s_temp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s_temp.connect(("8.8.8.8", 80))
        local_ip = s_temp.getsockname()[0]
    except Exception:
        local_ip = "127.0.0.1"
    finally:
        s_temp.close()

    # --- Criar servidor ---
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(5)

    print("===============================================")
    print("🚀 Servidor HTTP ativo!")
    print(f"  ➜ Localhost: http://localhost:{PORT}")
    print(f"  ➜ Rede local: http://{local_ip}:{PORT}")
    print("===============================================")

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
                method, route, _ = request_line.split(b' ')  # Ex: b'GET /adicionar HTTP/1.1'
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
        #Finalizando o Socket
        s.close()


if __name__ == "__main__":
    start_server()
