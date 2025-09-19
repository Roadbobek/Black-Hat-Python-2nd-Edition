# A simple tool based off the TCP Client seen in Black Hat Python 2nd Edition Chapter 2 Pages 10-11.
# I made this because I was curious about the HTML seen in the response and wanted to see it quickly without pasting it into a new file.
# This tool only works for web servers supporting HTTP traffic.

import socket
import os
import webbrowser
import datetime

# Specify target.
# Note, www.website.com and website.com can be different things, for example google.com is a redirect to www.google.com, but this script won't redirect you like a web browser.
# Note, the target server has to support HTTP traffic.
target_host = ("www.google.com")
target_port = 80 # Standard port for HTTP

print("Starting...")

# Create our client socket object.
# The AF_INET parameter indicates we’ll use a standard IPv4 address or hostname,
# and SOCK_STREAM indicates that this will be a TCP client.
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print("Connecting to target.")

# Connect our client to the target.
client.connect((target_host, target_port))

print("Sending data to target.")
print()

# Create a message to send to the target.
# Create an HTTP GET request to the target host.
# 'GET / HTTP/1.1' requests the homepage.
# '\r\n' separates the request line from the headers.
# 'Host:' is required for HTTP/1.1 to specify the domain.
# '\r\n\r\n' ends the request headers.
# \r (Carriage Return): This code moves the cursor back to the very beginning of the current line, without moving down.
# \n (Line Feed): This code moves the cursor down to the next line, without moving it horizontally.
client_message = f"GET / HTTP/1.1\r\nHost: {target_host}\r\n\r\n"

# Send our message to the target as utf-8 encoded bytes.
client.send(bytes(client_message, 'utf-8'))

# This tells the server that the client has finished sending data, so eventually,
# conn.recv(1024) on the server will return an empty string, allowing the loop to break.
client.shutdown(socket.SHUT_WR)

# Create an empty list and append the first response to it.
full_response = []

# Initiate a while loop that runs while we get a response back from the target.
while True:
    # Get next part of the response.
    last_response = client.recv(4096)
    # exit loop is no more data is received.
    if not last_response:
        break
    print(f"Received response chunk of length {len(last_response)}.")
    # Append it to our list.
    full_response.append(last_response)

# Cleanup, close the client socket.
client.close()

# If no data is received exit the program.
if full_response:
    print("All data received from target.")
    print()
else:
    print("No data received from target, exiting...")
    exit(0)

print("  Full raw response from target  ".center(120, '─'))
print()

# Print full raw response
print(full_response)
print()

# Combine the byte strings from the list into a single formated byte string.
full_response_bytes = b"".join(full_response)

print("  Full formated response from target  ".center(120, '─'))
print()

# Print the decoded data we got back from the target.
# We need to decode it to show properly.
print(full_response_bytes.decode())

# Get just the HTML from the decoded response and print it.
# Get starting character of the HTML in response.
html_start = full_response_bytes.decode().find("<!doctype html>".casefold())
if not html_start:
    html_start = full_response_bytes.decode().find("<html>".casefold())
elif not html_start:
    html_start = full_response_bytes.decode().find("<html".casefold())
# Get ending character of the HTML in response.
html_end = full_response_bytes.decode().find("</html>".casefold())
if html_end:
    html_end += 7
if not html_end:
    html_end = full_response_bytes.decode().find("</body>".casefold())

print("  HTML from target response  ".center(120, '─'))
print()

response_html = full_response_bytes.decode()[html_start:html_end]

if response_html:
    print(response_html)
    print()
else:
    print("No HTML found in response.")
    exit(0)

# Create a folder to store each HTML document.
if not os.path.exists("TCP-Client-Storage"):
    os.mkdir("TCP-Client-Storage")

# Get current time and format it for file name.
time_stamp = str(datetime.datetime.now()).replace(" ", ".").replace("-", ".").replace(":", ".")

# Store the HTML document in its own file.
with open(f'TCP-Client-Storage/TCP-Client-HTML-Response-{target_host}-{time_stamp}.html', 'w') as f:
    data = response_html
    f.write(data)

# Open the HTML document in a new web browser tab.
webbrowser.open_new_tab(f"file://{os.path.realpath(f"TCP-Client-Storage/TCP-Client-HTML-Response-{target_host}-{time_stamp}.html")}")

# # Add an input so it doesn't automatically exit.
# input("  Done, Press ENTER to exit.  ".center(120, '─'))