import socket

BUFFER_SIZE = 64

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 8888))
s.send('Hello world'.encode('utf-8'))
data = s.recv(BUFFER_SIZE)
print("Received message: '" + data.decode('utf-8') + "'")
s.close()
