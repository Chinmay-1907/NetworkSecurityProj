import socket
import threading
from cryptography.fernet import Fernet
import sys

# Configuration
HOST = '127.0.0.1'  # localhost
PORT = 5555        # arbitrary non-privileged port

class ChatClient:
    def __init__(self):
        self.client_socket = None
        self.fernet = None
        self.username = None
        self.connected = False
        self.receive_thread = None
    
    def connect_to_server(self):
        """Establish connection to the chat server"""
        try:
            # Create socket
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((HOST, PORT))
            
            # Receive encryption key from server
            key = self.client_socket.recv(1024)
            self.fernet = Fernet(key)
            print("Connected to server. Encryption established.")
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def authenticate(self):
        """Handle the authentication process"""
        try:
            # Receive username prompt
            encrypted_prompt = self.client_socket.recv(1024)
            username_prompt = self.fernet.decrypt(encrypted_prompt).decode()
            print(username_prompt, end='')
            
            # Send encrypted username
            self.username = input()
            self.client_socket.send(self.fernet.encrypt(self.username.encode()))
            
            # Receive password prompt
            encrypted_prompt = self.client_socket.recv(1024)
            password_prompt = self.fernet.decrypt(encrypted_prompt).decode()
            print(password_prompt, end='')
            
            # Send encrypted password
            password = input()
            self.client_socket.send(self.fernet.encrypt(password.encode()))
            
            # Receive authentication result
            encrypted_result = self.client_socket.recv(1024)
            result = self.fernet.decrypt(encrypted_result).decode()
            print(result)
            
            # Check if authentication was successful
            if "Welcome" in result:
                self.connected = True
                return True
            else:
                return False
        except Exception as e:
            print(f"Authentication error: {e}")
            return False
    
    def receive_messages(self):
        """Continuously receive and display messages from the server"""
        while self.connected:
            try:
                # Receive encrypted message
                encrypted_message = self.client_socket.recv(1024)
                if not encrypted_message:
                    break
                
                # Decrypt and display message
                message = self.fernet.decrypt(encrypted_message).decode()
                print(message)
            except Exception as e:
                print(f"Error receiving message: {e}")
                self.connected = False
                break
    
    def send_message(self, message):
        """Encrypt and send a message to the server"""
        try:
            encrypted_message = self.fernet.encrypt(message.encode())
            self.client_socket.send(encrypted_message)
            return True
        except Exception as e:
            print(f"Error sending message: {e}")
            self.connected = False
            return False
    
    def start(self):
        """Start the chat client"""
        # Connect to server
        if not self.connect_to_server():
            return
        
        # Authenticate
        if not self.authenticate():
            self.client_socket.close()
            return
        
        # Start message receiving thread
        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.daemon = True
        self.receive_thread.start()
        
        # Main message sending loop
        print("\nStart chatting (type 'exit' to quit):")
        while self.connected:
            try:
                message = input()
                if message.lower() == 'exit':
                    break
                if not self.send_message(message):
                    break
            except KeyboardInterrupt:
                break
        
        # Clean up
        self.connected = False
        if self.client_socket:
            self.client_socket.close()
        print("Disconnected from server.")

# Main execution
if __name__ == "__main__":
    client = ChatClient()
    client.start()