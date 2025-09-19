# Black Hat Python 2nd Edition
# Chapter 2, Pages 10-11
# --- TCP Client ---

import socket

# Specify target.
target_host = "www.google.com"
target_port = 80

# Create our client socket object.
# The AF_INET parameter indicates we’ll use a standard IPv4 address or hostname,
# and SOCK_STREAM indicates that this will be a TCP client.
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect our client to the target.
client.connect((target_host, target_port))

# Send some data from out client to the target (common sense).
client.send(b"GET / HTTP/1.1\r\nHost: google.com\r\n\r\n")

# Receive data back from target and store it in response.
response = client.recv(4096)

# Print the decoded data we got back from the target.
print(response.decode())

# Cleanup, close the client socket.
client.close()
