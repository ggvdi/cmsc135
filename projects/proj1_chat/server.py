import sys
import socket
import select
import utils

HOST = '127.0.0.1'
PORT = int(sys.argv[1])
BUFFER_SZ = 1024

sockets_list = []
channels_list = []
user_channel = {}
user_name = {}
s_socket = socket.socket()

def server(host, port):
    s_socket.bind((host, port))
    s_socket.listen(5)
    sockets_list.append(s_socket)
    
    print("Server started on port {}".format(port))
    while True:
        ready_to_read, ready_to_write, in_error = select.select(sockets_list, [], [], 0)
        for s in ready_to_read:
            if (s == s_socket):
                new_client, address = s.accept()
                new_client.send('<NAME>'.encode('ascii'))
                sockets_list.append(new_client)
            else:
                data = s.recv(BUFFER_SZ)
                if data:
                    msg = data.decode('ascii')
                    if msg[0] == '/':
                        handle_command(s, msg)
                    elif (not s in user_channel):
                        msg = utils.SERVER_CLIENT_NOT_IN_CHANNEL + "\n"
                        s.send(msg.encode('ascii'))
                    else:
                        announce_in_channel(user_channel[s], s, msg)
                else:
                    if s in sockets_list:
                        sockets_list.remove(s)
                    print("Client disconnected {}".format(s))
    s_socket.close()

def announce_in_channel(channel, sender, message):
    for s in sockets_list:
        if not s in user_channel:
            continue
        if s == sender:
            continue
        if user_channel[s] == channel:
            if sender in user_name:
                message = '[{}] '.format(user_name[sender]) + message
            s.send(message.encode('ascii'))

def handle_command(sender, message):
    args = message.split(" ", 1)
    cmd = args[0].strip(' \t\n\r')
    if cmd == "/join":
        if len(args) < 2:
            msg = utils.SERVER_JOIN_REQUIRES_ARGUMENT + "\n"
            sender.send(msg.encode('ascii'))
        else:
            c_name = args[1].strip(' \t\n\r')
            if c_name in channels_list:
                u_name = user_name[sender]
                left_channel = False
                if sender in user_channel:
                    left_channel = user_channel[sender]
                msg = utils.SERVER_CLIENT_JOINED_CHANNEL.format(u_name) + "\n"
                announce_in_channel(c_name,s_socket, msg)
                user_channel[sender] = c_name
                if left_channel:
                    msg = utils.SERVER_CLIENT_LEFT_CHANNEL.format(u_name) + "\n"
                    announce_in_channel(left_channel, s_socket, msg)
            else:
                msg = utils.SERVER_NO_CHANNEL_EXISTS.format(c_name) + "\n"
                sender.send(msg.encode('ascii'))
    elif cmd == '/create':
        if len(args) < 2:
            msg = utils.SERVER_CREATE_REQUIRES_ARGUMENT + "\n"
            sender.send(msg.encode('ascii'))
        else:
            c_name = args[1].strip(' \t\n\r')
            if c_name in channels_list: 
                msg = utils.SERVER_CHANNEL_EXISTS.format(c_name) + "\n"
                sender.send(msg.encode('ascii'))
            else:
                channels_list.append(c_name)
                print("Created channel " + c_name)
                left_channel = False
                if sender in user_channel:
                    left_channel = user_channel[sender]
                user_channel[sender] = c_name
                if left_channel:
                    u_name = user_name[sender]
                    msg = utils.SERVER_CLIENT_LEFT_CHANNEL.format(u_name) + "\n"
                    announce_in_channel(left_channel, s_socket, msg)
    elif cmd == '/list':
        msg = ''
        for channel in channels_list:
            msg += channel + "\n"
        sender.send(msg.encode('ascii'))
    elif cmd == '/name' and (not sender in user_name):
        user_name[sender] = args[1].strip(' \t\n\r')
        print('New user with name ' + user_name[sender])
    else:
        msg = utils.SERVER_INVALID_CONTROL_MESSAGE.format(cmd[1:]) + "\n"
        sender.send(msg.encode('ascii'))

if __name__ == "__main__":
    server(HOST, PORT)
