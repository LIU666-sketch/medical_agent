import socket

def send_audiofile(file_path):
    # 连接到开发板的服务器
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("192.168.137.100", 9999))  # 开发板的IP和端口

    # 读取文件并发送
    with open(file_path, 'rb') as f:
        sock.sendall(f.read())

    # 关闭连接
    sock.close()

def receive_result():
    # 连接到开发板的结果返回端口
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("0.0.0.0", 9998))  # 本机的IP和端口
    sock.listen(1)

    print("Waiting for result from the development board...")
    conn, addr = sock.accept()
    print("Connection from:", addr)

    result_data = b''
    while True:
        packet = conn.recv(4096)
        if not packet:
            break
        result_data += packet

    conn.close()
    audio_result = result_data.decode('utf-8')
    return audio_result
