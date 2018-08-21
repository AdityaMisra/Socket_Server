from socket import *
import time
import config
import os

class Server_Info:
    def __init__(self, name, address):
        self.name = name
        self.address = address
    # Compares objects for values inside, not a literal comparison
    def __eq__(self, other):
        return self.__dict__ == other.__dict__

class File_Transfer:
    def __init__(self, directory):
        # if \Example, add exact path 
        if directory.startswith("\\"):
            directory = os.path.dirname(os.path.realpath(__file__)) + directory
        self.directory = directory

        # Create folder
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    def get_files(self):
        files = []
        for filename in os.listdir(self.directory):
            try:
                files.append(open(self.directory+"\\"+filename, "rb"))
            except PermissionError:
                pass
        return files

class Connection:
    def __init__(self, port):
        self.port = port
        self.BROADCAST_INIT = 'broadcast'
        self.CONNECTED      = 'connected'

        ''' Sending Socket '''
        self.send_sock = socket(AF_INET, SOCK_DGRAM)
        self.send_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.send_sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.send_sock.settimeout(5.0)
    
    def host(self):
        ''' Host Global Socket '''
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.bind(('', self.port))
        found_clients = []
        ft = File_Transfer(config.HOST_DIR)

        print("Server Started...")

        while True:
            data, address = sock.recvfrom(1024)
            data = str(data.decode('UTF-8'))

            # Provide server infomation            
            if data == self.BROADCAST_INIT:
                responce = 'res:' + config.SERVER_NAME
                sent = sock.sendto(responce.encode(), address)
                if str(address) not in found_clients:
                    print("Gave " + str(address) + " server details")
                    found_clients.append(str(address))

            # Return Public Folder Content
            if data == self.CONNECTED:
                files = ft.get_files()
                if len(files) < 1: sent = sock.sendto(self.CONNECTED.encode(), address) # No files to send
                else:
                    for f in files:
                        print("Sending: " + f.name)
                        sock.sendto(("file:" + os.path.basename(f.name)).encode(), address)
                        l = f.read(1024)
                        while (l):
                            sock.sendto(l, address)
                            l = f.read(1024)
                        f.close()
                        sock.sendto(("end").encode(), address)
                    
                
    def search(self):
        ''' Find Global Servers'''
        server_address = ('255.255.255.255', self.port)
        servers = []
        search_interval = 5
        start_time = time.time()
        while time.time() < (start_time + search_interval):
            # Query for servers - ask network for information
            sent = self.send_sock.sendto(self.BROADCAST_INIT.encode(), server_address)
            data, server = self.send_sock.recvfrom(1024)
            data = data.decode('UTF-8')
            if data.startswith('res:') and Server_Info(data[4:], server) not in servers:
                servers.append(Server_Info(data[4:], server[0]))
        return servers

    def connect(self, ip):
        ''' Establish a Connection to Server '''
        directory = config.CLIENT_DIR
        # if \Example, add exact path 
        if directory.startswith("\\"):
            directory = os.path.dirname(os.path.realpath(__file__)) + directory
        # Create Container Folder
        if not os.path.exists(directory):
            os.makedirs(directory)
        print("Connecting")
        while True:
            sent = self.send_sock.sendto(self.CONNECTED.encode(), (ip, self.port))
            data = self.send_sock.recv(1024)
            command = data.decode('UTF-8')

            # Idle
            if command == self.CONNECTED:
                print("idle")

            # Receiving File!
            if command.startswith('file:'):
                print("Receiving...")
                data = self.send_sock.recv(1024)
                f = open(directory+"\\"+command[5:],'wb')
                i = 0
                while data:
                    try:
                        if data.decode('UTF-8') == "end":
                            break
                    except Exception:
                        pass
                    f.write(data)
                    data = self.send_sock.recv(1024)
                f.close()

            
con = Connection(config.PORT)
