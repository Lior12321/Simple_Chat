# Advanced Multi-User Chat - Socket Programming Project
```
This project implements a multi-user chat system using socket programming in Python.
It consists of three main components: a server, a client, and a protocol handler.
The system supports multiple clients communicating simultaneously with features like naming, messaging, blocking users, and broadcasting messages.
```

---

## 📂 Project Structure

```
Simple_Chat/
├── client.py          # Client-side application for connecting to the chat server
├── server.py          # Server-side application managing multiple client connections
├── protocol.py        # Protocol implementation handling message formatting and parsing
├── test 3 clients.png # Screenshot showing the project running
└── README.md          # This documentation file
```
---

## 🎯 Features and Commands Supported

- **NAME <name>**  
  Sets the client's username. The server replies with `HELLO <name>` if successful, or an error if the name is already taken.

- **GET_NAMES**  
  Requests a list of all currently connected client names.

- **MSG <NAME> <message>**  
  Sends a message to a specific client by name.  
  Special name `BROADCAST` sends the message to all clients except the sender.

- **BLOCK <name>**  
  Blocks messages from a specific user.

- **EXIT**  
  Disconnects the client from the server.

---

## 📊 How It Works

- The server handles multiple clients simultaneously, managing their names and message routing.
- The client supports non-blocking input and message receiving using Python's `select` module and `msvcrt` for Windows.
- A length field is included in the protocol messages to ensure full message receipt.
- If an invalid command or target client is specified, the server sends an appropriate error response.

---

## 🛠 Running the Project

1. Run the server:
   ```
   python server.py
   ```
2. Run one or more clients (each in a separate terminal):
	```
	python client.py
	```
3. Use the supported commands (NAME, MSG, GET_NAMES, BLOCK, EXIT) to interact in the chat.

---

## 📄 Notes

* The project was developed as part of an advanced socket programming exercise by Lior Masas.

* The client supports multiple simultaneous connections and message routing.

* The server maintains mappings between client sockets and their usernames for efficient message delivery.


