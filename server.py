# Lior Masas - 315402453
import socket
import select
import protocol
import re

SERVER_PORT = 8888
SERVER_IP = "0.0.0.0"
global clients_names
client_block = {}

def handle_client_request(current_socket, clients_names, data, client_sockets):
    messages_to_send = []
    reply = ""
    dest_socket = current_socket
    new_messages = []

    commands = ("NAME", "GET_NAMES", "MSG", "BLOCK", "EXIT")
    parts = data.split(" ", 2)
    command = parts[0]
    args = parts[1] if len(parts) > 1 else ""    # commands dictionary
    # check if the command is in the dictionary
    if command not in commands:
        reply = f"ERROR - Unknown command: {command}"
        return reply, dest_socket, new_messages


    # set the name of the client
    if command == "NAME":
        if len(parts) != 2:
            reply = "ERROR - invalid request"
        if args == "":
            reply = "ERROR - name is missing"
        elif args == "BROADCAST":
            reply = f"ERROR - the name {args} is not allowed"
        # the name needs to contain only letters and no spaces or special characters (using regular expression)
        elif not re.fullmatch(r"[A-Za-z]+", args):
            reply = f"ERROR - the name {args} is invalid. Only English letters are allowed."
        elif args in clients_names.keys():
            reply = f"ERROR - the name {args} is already taken"
        else:
            clients_names[args] = current_socket
            reply = f"hello {args}"
        return reply, dest_socket, new_messages


    # get the names of all connected clients
    elif command == "GET_NAMES":
        if len(parts) > 1:
            reply = "ERROR - invalid request"
            return reply, dest_socket, new_messages
        names = list(clients_names.keys())
        reply = "Connected users: " + " ".join(names) if names else "No users connected."
        return reply, dest_socket, new_messages


    # send a message to a specific client or broadcast a message to all clients
    elif command == "MSG":
        if len(parts) != 3:
            reply = "ERROR - invalid message"
            return reply, dest_socket, messages_to_send
        name, msg = parts[1], parts[2]
        sender_name = next((k for k, v in clients_names.items() if v == current_socket), None)

        # check if the name is only one word
        if not re.fullmatch(r"[A-Za-z]+", msg):
            reply = "ERROR - the message must be a single word with no spaces or special characters."
            return reply, dest_socket, messages_to_send

        # broadcast message to all clients except the sender and blocked clients
        if name == "BROADCAST":
            _, message = data.split(" ", 1)
            sender_name = list(clients_names.keys())[list(clients_names.values()).index(current_socket)]
            reply = f"{sender_name} broadcasted: {message}"
            dest_socket = None  # Broadcast to all except the sender
            for client, socket in clients_names.items():
                if client != sender_name and sender_name not in client_block.get(client, []):
                    messages_to_send.append((socket, reply))
            return reply, dest_socket, messages_to_send

        # send message to specific client
        elif name in clients_names:
            if sender_name in client_block.get(name, []):
                reply = f"ERROR - {name} blocked you."
            else:
                dest_socket = clients_names[name]
                reply = f"{sender_name} sent: {msg}"
        # client not found
        else:
            reply = f"ERROR - {name} not found"
        return reply, dest_socket, messages_to_send


    # block a client from sending messages to the client who sent the block command
    elif command == "BLOCK":
        if len(parts) != 2:
            return "ERROR - invalid request. no user entered or too many arguments", None, []
        if args not in clients_names:
            return f"ERROR - {args} not found", None, []
        else: # add the blocked client to the block list
            sender_name = list(clients_names.keys())[list(clients_names.values()).index(current_socket)]
            if sender_name not in client_block:
                client_block[sender_name] = []
            client_block[sender_name].append(args)
            reply = f"{sender_name} blocked {args}"
            return reply, dest_socket, messages_to_send


    # close the connection with the client and remove him from the list
    elif command == "EXIT":
        if len(parts) > 1:
            return "ERROR - invalid request", None, []
        sender_name = next((k for k, v in clients_names.items() if v == current_socket), None)
        if sender_name:
            print(f"{sender_name} has disconnected.")
            del clients_names[sender_name]
        if current_socket in client_sockets:
                client_sockets.remove(current_socket)
        messages_to_send = [messege for messege in messages_to_send if messege[0] != current_socket]
        current_socket.close()
        return "", dest_socket, messages_to_send

    else:
        return "ERROR - Invalid request", dest_socket, messages_to_send


def print_client_sockets(client_sockets):
    for c in client_sockets:
        print("\t", c.getpeername())


def main():
    print("Setting up server")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    print("Listening for clients")
    server_socket.listen()
    client_sockets = []
    messages_to_send = []
    clients_names = {}
    while True:
        read_list = client_sockets + [server_socket]
        ready_to_read, ready_to_write, in_error = select.select(read_list, client_sockets, [])
        for current_socket in ready_to_read:
            if current_socket is server_socket:
                client_socket, client_address = server_socket.accept()
                print("Client joined!\n", client_address)
                client_sockets.append(client_socket)
                print_client_sockets(client_sockets)
            else:
                print("Data from client:")
                data = protocol.get_message(current_socket)
                if data == "":
                    print("Connection closed\n")
                    for entry in clients_names.keys():
                        if clients_names[entry] == current_socket:
                            sender_name = entry
                    clients_names.pop(sender_name)
                    client_sockets.remove(current_socket)
                    current_socket.close()
                else:
                    print(data + "\n")
                    (response, dest_socket, new_messages) = handle_client_request(current_socket, clients_names, data, client_sockets)
                    if response:  # add the response only if it is not empty
                        messages_to_send.append((dest_socket, response))
                    messages_to_send.extend(new_messages)

        # write to everyone (note: only ones which are free to read...)
        for message in messages_to_send:
            current_socket, data = message
            if current_socket in ready_to_write:
                response = protocol.create_msg(data)
                current_socket.send(response)
                messages_to_send.remove(message)

if __name__ == '__main__':
    main()