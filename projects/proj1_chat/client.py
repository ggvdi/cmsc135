import sys
import socket
import select

NAME = sys.argv[1]
HOST = sys.argv[2]
PORT = int(sys.argv[3])

def client(name, host, port):
    c_socket = socket.socket()
    try:
        c_socket.connect((host, port))
    except:
        msg = "Unable to connect to {0}:{1}".format(host, port)
        print(msg)
        sys.exit()
    sockets_list = [sys.stdin, c_socket]
    while True:
        ready_to_read,ready_to_write,in_error = select.select(sockets_list, [], [], 0)
        for sock in ready_to_read:
            if sock == c_socket:
                data = sock.recv(1024)
                if data:
                    msg = data.decode('ascii')
                    if msg == '<NAME>':
                        sendback = '/name ' + NAME
                        c_socket.send(sendback.encode('ascii'))
                    else:
                        print(msg, end='\r')
                else:
                    msg = "Server at {0}:{1} has disconnected".format(host, port)
                    print(msg)
                    sys.exit()
            else:
                msg = sys.stdin.readline()
                st = "[Me] " + msg
                sys.stdout.write("\033[F")
                print(st, end='\r')
                c_socket.send(msg.encode('ascii'))

if __name__ == "__main__":
    sys.exit(client(NAME, HOST, PORT))

