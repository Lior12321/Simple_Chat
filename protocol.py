# Lior Masas - 315402453

number_of_bytes = 4

def create_msg(data):
    """
    Encodes a message with its length prefix.
    """
    try:
        data = data.strip()
        length = len(data.encode('utf-8')).to_bytes(number_of_bytes, 'big')
        return length + data.encode('utf-8')
    except Exception as e:
        print(f"Error encoding message: {e}")
        return b""


def get_message(sock):
    """
    Decodes a message received over a socket.
    """
    try:
        # Read the first 4 bytes for the message length
        length_data = sock.recv(number_of_bytes)
        if len(length_data) < number_of_bytes:
            pass

        length = int.from_bytes(length_data, 'big')
        # Read the message in chunks until the full message is received
        data = sock.recv(length)
        if len(data) < length:
            raise Exception("Received incomplete data")

        return data.decode()
    except Exception as e:
        print(f"Error: {e}")
        return ""