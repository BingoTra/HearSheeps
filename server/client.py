import socket



sock = socket.socket()
sock.connect(('localhost', 9090))
while True:
    sock.send(input().encode())
    data = sock.recv(1024).decode()
    print(data)
