import socket
import threading
import sqlite3
import datetime
from cryptography.fernet import Fernet

# Configuration
HOST = '127.0.0.1'  # localhost
PORT = 5555        # arbitrary non-privileged port

# Hard-coded user credentials for demo purposes
# In a production environment, these would be stored securely (hashed + salted)
USERS = {
    "user1": "pass1"
}

# Generate or load encryption key
# In a production environment, this would be securely stored and distributed
# For a real system, you would implement RSA key exchange here to prevent MITM attacks
KEY = Fernet.generate_key()
fernet = Fernet(KEY)

# Set up database for encrypted message logging
def setup_database():
    conn = sqlite3.connect('chat_logs.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        username TEXT,
        encrypted_message BLOB
    )
    ''')
    conn.commit()
    conn.close()

# Log message to database (encrypted)
def log_message(username, message):
    encrypted_message = fernet.encrypt(message.encode())
    timestamp = datetime.datetime.now().isoformat()
    
    conn = sqlite3.connect('chat_logs.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (timestamp, username, encrypted_message) VALUES (?, ?, ?)",
        (timestamp, username, encrypted_message)
    )
    conn.commit()
    conn.close()

# Handle individual client connection
def handle_client(client_socket, client_address):
    # Authentication phase
    client_socket.send(fernet.encrypt(b"Username: "))
    encrypted_username = client_socket.recv(1024)
    username = fernet.decrypt(encrypted_username).decode()
    
    client_socket.send(fernet.encrypt(b"Password: "))
    encrypted_password = client_socket.recv(1024)
    password = fernet.decrypt(encrypted_password).decode()
    
    # Validate credentials
    if username not in USERS or USERS[username] != password:
        client_socket.send(fernet.encrypt(b"Authentication failed. Connection closed."))
        client_socket.close()
        print(f"Failed authentication attempt from {client_address}")
        return
    
    # Authentication successful
    welcome_message = f"Welcome, {username}! You are now connected."
    client_socket.send(fernet.encrypt(welcome_message.encode()))
    
    # Broadcast user joined
    broadcast_message = f"{username} has joined the chat!"
    broadcast(broadcast_message, username)
    log_message("SERVER", broadcast_message)
    print(f"{username} connected from {client_address}")
    
    # Main message handling loop
    while True:
        try:
            # Receive encrypted message
            encrypted_data = client_socket.recv(1024)
            if not encrypted_data:
                break
            
            # Decrypt message
            message = fernet.decrypt(encrypted_data).decode()
            
            # Log the message
            log_message(username, message)
            
            # Format and broadcast message
            formatted_message = f"{username}: {message}"
            print(formatted_message)
            broadcast(formatted_message, username)
            
        except Exception as e:
            print(f"Error handling client {username}: {e}")
            break
    
    # Client disconnected
    disconnect_message = f"{username} has left the chat."
    broadcast(disconnect_message, username)
    log_message("SERVER", disconnect_message)
    print(f"{username} disconnected")
    client_socket.close()
    clients.remove((client_socket, username))

# Broadcast message to all authenticated clients
def broadcast(message, sender_username):
    encrypted_message = fernet.encrypt(message.encode())
    for client_socket, username in clients:
        # Don't send message back to the sender
        if username != sender_username:
            try:
                client_socket.send(encrypted_message)
            except:
                # If sending fails, the client is likely disconnected
                client_socket.close()
                clients.remove((client_socket, username))

# Main server function
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    
    print(f"Server started on {HOST}:{PORT}")
    print(f"Encryption key: {KEY.decode()}")
    print("Waiting for connections...")
    
    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")
        
        # Send encryption key to client
        # NOTE: In a production environment, you would use asymmetric encryption (RSA)
        # to securely exchange the symmetric key to prevent MITM attacks
        client_socket.send(KEY)
        
        # Start a new thread to handle the client
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.daemon = True
        client_thread.start()

# Initialize global variables
clients = []

# Main execution
if __name__ == "__main__":
    setup_database()
    start_server()