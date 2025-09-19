import socket

target_host = "127.0.0.1"
target_port = 9998

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect((target_host, target_port))

while True:
    msg = input("message or EXIT: ")
    if msg == "EXIT":
        break
    client.send(bytes(msg, 'utf-8'))

response = client.recv(4096)
print(response.decode())

client.close()