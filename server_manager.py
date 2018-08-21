from socket import *
import time
import config

class Connection_Start:
    def __init__(self, port):
        self.port = port
        self.broadcast_msg = 'broadcast'
        self.connect_msg   = 'connect'
    
    def host(self):
        ''' Scan Global Sockets '''
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.bind(('', self.port))
        found_clients = []

        while True:
            data, address = sock.recvfrom(4096)
            data = str(data.decode('UTF-8'))

            # Respond to client            
            if data == self.broadcast_msg:
                responce = 'res:' + config.SERVER_NAME
                sent = sock.sendto(responce.encode(), address)
                if str(address) not in found_clients:
                    print(str(address) + " - Gave server info")
                    found_clients.append(str(address))

            # Connect to client
            if data == self.connect_msg:
                responce = 'res:yes'
                sent = sock.sendto(responce.encode(), address)
                
    def search(self):
        ''' Start Global Socket '''
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        server_address = ('255.255.255.255', self.port)

        servers = []
        start_time = time.time()

        print('Searching for File Servers...')
        try:
            while time.time() < start_time + 5:
                # Query
                sent = sock.sendto(self.broadcast_msg.encode(), server_address)
                data, server = sock.recvfrom(4096)
                if data.decode('UTF-8').startswith('res:') and str(server[0]) not in servers:
                    print('Found Server at: ' + str(server[0]))
                    servers.append(str(server[0]))
        finally:	
                sock.close()
        return servers

    def connect(self, address):
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        server_address = (address, config.PORT)
        
        while True:
            sent = sock.sendto(self.connect_msg.encode(), server_address)
            data, server = sock.recvfrom(4096)
            print(data.decode('UTF-8'))
            
    
con = Connection_Start(config.PORT)
