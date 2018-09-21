import socket

BUFFER_SIZE = 64

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('127.0.0.1', 8888))
s.listen(1)

conn, addr = s.accept()
data = conn.recv(BUFFER_SIZE)
print("Received message: '" + data.decode('utf-8') + "'")
conn.send('Hi'.encode('utf-8'))
conn.close()
