# Lior Masas - 315402453
import socket
import threading
import select
import msvcrt
import chat_server_skeleton
import protocol

# NAME <name> will set name. Server will reply error if duplicate
# GET_NAMES will get all names
# MSG <NAME> <message> will send message to client name or to broadcast
# BLOCK <name> will block a user from sending messages to the client who sent the block command
# EXIT will close client

my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
my_socket.connect(("127.0.0.1", 8888))
print("Enter commands\n")
msg = ""
closing = False  # flag to indicate if the client is closing

# Function to receive messages from the server
def receive_messages():
    global closing
    while not closing:
        try:
            rlist, _, _ = select.select([my_socket], [], [], 0.2)
            if rlist:
                # receive the message from the server
                data = protocol.get_message(my_socket)
                if not data:
                    closing = True
                    break
                print("Server sent: " + data + "\n")
        except OSError:
            if not closing:
                print("Error: Socket closed unexpectedly")
            closing = True
            break
        except Exception as e:
            if not closing:
                print(f"Error receiving message: {e}")
            closing = True
            break

# Run the receive_messages function in a separate thread
try:
    thread = threading.Thread(target=receive_messages, daemon=True)
    thread.start()

    # Main loop to send messages to the server
    while msg != "EXIT":
        if closing:
            print("Connection closed")
            break
        if msvcrt.kbhit(): #check if a key was pressed
            msg = ""
            while True:
                key = msvcrt.getch()
                if key == b'\x00' or key == b'\xe0':
                    special_key = msvcrt.getch()
                    continue
                try:
                    key = key.decode("utf-8")
                # Ignore any non-ASCII characters
                except UnicodeDecodeError:
                    continue
                if key == '\r': # Enter key pressed
                    print("\n")
                    if msg.strip(): # The message is not empty
                        my_socket.sendall(protocol.create_msg(msg))
                        break
                elif key == '\b': # Backspace key pressed
                    msg = msg[:-1]
                    print("\b \b", end="", flush=True)
                else:
                    msg += key
                    print(key, end="", flush=True)

finally:
    # Set the closing flag to True to stop the receive_messages thread
    closing = True
    thread.join()
    my_socket.close()
    print("Client closed")