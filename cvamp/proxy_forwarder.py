import socket
import threading
import select
import socketserver
import base64
import struct
from urllib.parse import urlparse


class Socks5ProxyHandler(socketserver.BaseRequestHandler):
    """
    HTTP proxy server that forwards requests to a SOCKS5 proxy with authentication
    """
    
    def __init__(self, request, client_address, server):
        self.socks_host = server.socks_host
        self.socks_port = server.socks_port
        self.socks_username = server.socks_username
        self.socks_password = server.socks_password
        super().__init__(request, client_address, server)
    
    def handle(self):
        try:
            # Read the HTTP CONNECT request
            request = self.request.recv(4096).decode('utf-8', errors='ignore')
            
            if request.startswith("CONNECT"):
                # Parse the CONNECT request
                lines = request.split('\n')
                host_port = lines[0].split(' ')[1]
                target_host, target_port = host_port.split(':')
                target_port = int(target_port)
                
                # Establish connection to SOCKS5 proxy
                socks_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                socks_socket.connect((self.socks_host, self.socks_port))
                
                # SOCKS5 handshake with authentication
                # Version identifier/method selection request
                socks_socket.sendall(b'\x05\x02\x00\x02')  # Version 5, 2 methods: no auth and username/password
                
                # Get method selection response
                method_response = socks_socket.recv(2)
                if method_response[0] != 5 or method_response[1] != 2:
                    # No auth (0) or other method selected, continue without auth
                    socks_socket.close()
                    self.request.sendall(b'HTTP/1.1 502 Bad Gateway\r\n\r\n')
                    return
                
                # Username/password authentication
                username_bytes = self.socks_username.encode('utf-8')
                password_bytes = self.socks_password.encode('utf-8')
                
                auth_request = bytearray()
                auth_request.append(1)  # Version
                auth_request.append(len(username_bytes))
                auth_request.extend(username_bytes)
                auth_request.append(len(password_bytes))
                auth_request.extend(password_bytes)
                
                socks_socket.sendall(auth_request)
                
                # Get auth response
                auth_response = socks_socket.recv(2)
                if auth_response[0] != 1 or auth_response[1] != 0:  # Version 1, status 0 (success)
                    socks_socket.close()
                    self.request.sendall(b'HTTP/1.1 502 Bad Gateway\r\n\r\n')
                    return
                
                # Send CONNECT request to SOCKS5 proxy
                target_host_bytes = target_host.encode('utf-8')
                
                connect_request = bytearray()
                connect_request.append(5)  # Version
                connect_request.append(1)  # CONNECT
                connect_request.append(0)  # Reserved
                connect_request.append(3)  # Address type (DOMAINNAME)
                connect_request.append(len(target_host_bytes))
                connect_request.extend(target_host_bytes)
                connect_request.extend(struct.pack('>H', target_port))
                
                socks_socket.sendall(connect_request)
                
                # Get connection response
                response = socks_socket.recv(1024)
                if response[0] != 5 or response[1] != 0:  # Version 5, status 0 (success)
                    socks_socket.close()
                    self.request.sendall(b'HTTP/1.1 502 Bad Gateway\r\n\r\n')
                    return
                
                # Connection established - send success response to client
                self.request.sendall(b'HTTP/1.1 200 Connection Established\r\n\r\n')
                
                # Start bidirectional forwarding
                self.forward_data(self.request, socks_socket)
            else:
                # For other requests, the client should use direct HTTP proxy mode
                self.request.sendall(b'HTTP/1.1 405 Method Not Allowed\r\n\r\n')
        except Exception as e:
            print(f"Proxy error: {e}")
            try:
                self.request.sendall(b'HTTP/1.1 502 Bad Gateway\r\n\r\n')
            except:
                pass
    
    def forward_data(self, client_socket, server_socket):
        """Forward data bidirectionally between client and server"""
        try:
            while True:
                # Use select to handle both sockets
                ready, _, _ = select.select([client_socket, server_socket], [], [], 1)
                
                if client_socket in ready:
                    data = client_socket.recv(4096)
                    if not data:
                        break
                    server_socket.sendall(data)
                
                if server_socket in ready:
                    data = server_socket.recv(4096)
                    if not data:
                        break
                    client_socket.sendall(data)
        except:
            pass
        finally:
            client_socket.close()
            server_socket.close()


class Socks5ProxyServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    def __init__(self, server_address, socks_host, socks_port, username, password, bind_and_activate=True):
        self.socks_host = socks_host
        self.socks_port = socks_port
        self.socks_username = username
        self.socks_password = password
        
        # Disable socket reuse to avoid issues
        self.allow_reuse_address = True
        
        # Initialize the server without binding
        socketserver.TCPServer.__init__(self, server_address, Socks5ProxyHandler, bind_and_activate)


def create_socks5_forwarding_proxy(socks_url):
    """
    Create a local HTTP proxy that forwards to the given SOCKS5 proxy with authentication
    :param socks_url: socks5://username:password@host:port
    :return: server instance and local proxy URL
    """
    # Parse the SOCKS5 URL
    if not socks_url.startswith('socks5://'):
        raise ValueError("URL must start with socks5://")
    
    # Remove the protocol part
    no_protocol = socks_url[9:]  # Remove "socks5://"
    
    # Split at @ to separate auth from host:port
    if '@' not in no_protocol:
        raise ValueError("SOCKS5 URL must include authentication (username:password@host:port)")
    
    auth_part, host_port = no_protocol.split('@', 1)
    username, password = auth_part.split(':', 1)
    
    if ':' not in host_port:
        raise ValueError("Host:port format is required")
    
    host, port_str = host_port.split(':', 1)
    port = int(port_str)
    
    # Find an available port for the local proxy
    import socket
    from contextlib import closing
    
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.listen(1)
        local_port = s.getsockname()[1]
    
    # Create the proxy server
    server = Socks5ProxyServer(
        ("127.0.0.1", local_port),
        host, port, username, password
    )
    
    # Start the server in a separate thread
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    
    local_url = f"http://127.0.0.1:{local_port}"
    print(f"Local proxy server started: {local_url} -> {socks_url}")
    
    return server, local_url