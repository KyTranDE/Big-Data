import socket

HOST = 'localhost'
PORT = 9999
MESSAGE = 'Xin chào PySpark Streaming'

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(MESSAGE.encode('utf-8'))
