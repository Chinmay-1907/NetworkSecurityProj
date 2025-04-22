# Secure Encrypted Chat Application

A simple, secure chat application with encryption, authentication, and message logging. This project was developed as part of a Network Security course to demonstrate secure communication principles.

## Features

- **End-to-End Encryption**: All messages are encrypted using AES (Fernet) encryption
- **User Authentication**: Basic username/password authentication
- **Encrypted Message Logging**: All messages are logged in an encrypted SQLite database
- **Multiple Client Support**: Multiple clients can connect to a single server

## Requirements

- Python 3.7+
- cryptography library

## Installation

1. Clone this repository or download the source code
2. Install the required dependencies:

```
pip install -r requirements.txt
```

## Usage

### Starting the Server

Run the server script:

```
python server.py
```

The server will start on localhost (127.0.0.1) port 5555 and display the encryption key that will be used for the session.

### Connecting with a Client

Run the client script in a separate terminal:

```
python client.py
```

The client will automatically connect to the server running on localhost:5555.

### Authentication

When prompted, enter the following credentials:

- Username: `user1`
- Password: `pass1`

These credentials are hard-coded in the server for demonstration purposes.

### Chatting

Once authenticated, you can start sending messages. Any message you type will be encrypted, sent to the server, and then broadcast to all other connected clients.

To exit the chat, type `exit`.

### Multiple Clients

You can start multiple client instances in different terminals to simulate a multi-user chat environment.

## Inspecting Encrypted Logs

The server logs all messages to a SQLite database file named `chat_logs.db`. You can inspect this database using any SQLite browser or the SQLite command-line tool:

```
sqlite3 chat_logs.db
```

To view the encrypted messages:

```sql
SELECT * FROM messages;
```

To decrypt a message, you would need to use the encryption key displayed when starting the server and use the Fernet decrypt method in Python.

## Security Notes

This is a demonstration project and has several security limitations:

1. The encryption key is transmitted in plaintext when a client connects
2. In a production environment, you would use asymmetric encryption (RSA) for the initial key exchange
3. Passwords are not hashed or salted
4. There is no protection against replay attacks

## Project Structure

- `server.py`: The chat server that handles connections, authentication, and message broadcasting
- `client.py`: The chat client that connects to the server and provides a user interface
- `requirements.txt`: List of required Python packages
- `chat_logs.db`: SQLite database containing encrypted chat logs (created when the server runs)