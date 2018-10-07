from socket import *
from colorama import init, Fore
import time
import config
import os
import hashlib


init(autoreset=True)


class ServerInfo:
    def __init__(self, name, address):
        self.name = name
        self.address = address
    # Compares objects for values inside, not a literal comparison
    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class FileTransfer:
    def __init__(self, directory):
        # if \Example, add exact path 
        if directory.startswith("\\"):
            directory = os.path.dirname(os.path.realpath(__file__)) + directory
        self.directory = directory

        # Create folder
        if not os.path.exists(directory):
            os.makedirs(directory)

        self.file_history = []
        self.hash_to_remove = []

    @staticmethod
    def file_hash(file_dir):
        # Get file as a Hash (unique identifier)
        hash_md5 = hashlib.md5()
        try:
            with open(file_dir, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
        # File can be deleted during this (possibly causing OS/Perm error)
        except (FileNotFoundError, OSError, PermissionError):
            return None
        return hash_md5.hexdigest()

    def get_files_for_sending(self):
        files = []
        new_hashs = []
        # Get all files in Container folder
        for filename in os.listdir(self.directory):
            hash_ = FileTransfer.file_hash(self.directory + "\\" + filename)
            if hash_:
                new_hashs.append(hash_)
            # New File
            if hash_ and hash_ not in self.file_history:
                 files.append(open(self.directory+"\\"+filename, "rb"))
        for item in self.file_history:
            # Remove file
            if item not in new_hashs:
                self.hash_to_remove.append(item)
        
        self.file_history = new_hashs
        return files


class Connection:
    CONNECTING = 'CONNECTING'
    IDLE = 'IDLE'
    RECEIVING = 'RECEIVING'
    DELETING = 'DELETING'
    ERROR = 'ERROR'

    status_color_mapping = {
        CONNECTING: Fore.LIGHTBLUE_EX,
        IDLE: Fore.YELLOW,
        RECEIVING: Fore.LIGHTGREEN_EX,
        DELETING: Fore.RED,
        ERROR: Fore.LIGHTRED_EX
    }

    def __init__(self, port):
        self.port = port
        self.BROADCAST_INIT = '*'
        self.CONNECTED      = '&'
        
        ''' Sending Socket '''
        self.send_sock = socket(AF_INET, SOCK_DGRAM)
        self.send_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.send_sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.send_sock.settimeout(5.0)
    
    def host(self):
        """
        Host Global Socket
        :return:
        """

        sock = socket(AF_INET, SOCK_DGRAM)
        sock.bind(('', self.port))
        found_clients = []
        ft = FileTransfer(config.HOST_DIR)

        print(Fore.LIGHTGREEN_EX + "Server Started...")
    
        while True:
            data, address = sock.recvfrom(1024)
            data = str(data.decode('UTF-8'))

            # Provide server information
            if data == self.BROADCAST_INIT:
                response = 'res:' + config.SERVER_NAME
                sent_count = sock.sendto(response.encode(), address)

                if str(address) not in found_clients:
                    print(Fore.YELLOW + str(address) + Fore.LIGHTBLUE_EX +" - requested server details")
                    found_clients.append(str(address))

            # Return Public Folder Content
            if data == self.CONNECTED:
                files = ft.get_files_for_sending()
                file_amount = len(files)

                # Request Deletes
                for f in ft.hash_to_remove:
                    print(Fore.RED + "Delete Request for ")
                    sock.sendto(("del:" + os.path.basename(f.name)).encode(), address)
                
                # Send Files
                if file_amount < 1:
                    sent = sock.sendto(self.CONNECTED.encode(), address) # No files to send
                else:
                    # Send Files
                    for f in files:
                        print(Fore.LIGHTGREEN_EX + "Serving " +
                              Fore.YELLOW + address[0] +
                              Fore.LIGHTGREEN_EX + " - " + f.name)
                        sock.sendto(("file:" + os.path.basename(f.name)).encode(), address)
                        data_read = f.read(1024)
                        while data_read:
                            sock.sendto(data_read, address)
                            data_read = f.read(1024)
                        sock.sendto("end".encode(), address)
                        f.close() 
                        
    def search(self):
        """
         Find Global Servers
        :return:
        """

        print(Fore.LIGHTBLUE_EX + "*Searching for servers*")
        server_address = ('255.255.255.255', self.port)
        servers = []
        search_interval = 2 # seconds
        start_time = time.time()

        # Search as long as interval
        while time.time() < (start_time + search_interval):
            # Query for servers - ask network for information
            self.send_sock.sendto(self.BROADCAST_INIT.encode(), server_address)
            data, server = self.send_sock.recvfrom(1024)
            data = data.decode('UTF-8')
            if data.startswith('res:') and ServerInfo(data[4:], server[0]) not in servers:
                servers.append(ServerInfo(data[4:], server[0]))
                print("\t" + Fore.LIGHTWHITE_EX + str(len(servers)) + Fore.LIGHTGREEN_EX + " server/s found.")
        print("\n")
        return servers

    @staticmethod
    def clean_up(directory):
        # Clear files
        print(Fore.RED + "Purging - " + directory)
        try:
            for filename in os.listdir(directory):
                os.remove(directory+"\\"+filename)
        except Exception:
            pass

    def connect(self, ip):
        """
        Establish a Connection to Server
        :param ip:
        :return:
        """

        self.status = self.CONNECTING

        print(self.status_color_mapping[self.status] + "Connecting - " + Fore.LIGHTWHITE_EX + ip)
        directory = config.CLIENT_DIR

        # if \Example, add exact path
        if directory.startswith("\\"):
            directory = os.path.dirname(os.path.realpath(__file__)) + directory
        # Create Container Folder
        if not os.path.exists(directory):
            os.makedirs(directory)
        # Clear Folder
        else:
            self.clean_up(directory)

        # Initialise Connection
        while True:
            print("Status: " + self.status_color_mapping[self.status] + self.status, end="\r", flush=True)

            # Talk to server
            self.send_sock.sendto(self.CONNECTED.encode(), (ip, self.port))
            data = self.send_sock.recv(1024)
            command = data.decode('UTF-8')

            # Idle
            if command == self.CONNECTED:
                self.status = "IDLE"

            # Receiving File!
            elif command.startswith('file:'):
                self.status = self.RECEIVING
                data = self.send_sock.recv(1024)
                print(self.status_color_mapping[self.status] + "Receiving file: " +
                      Fore.LIGHTWHITE_EX + command[5:])

                f = open(directory+"\\"+command[5:],'wb')
                while data:
                    try:
                        if data.decode('UTF-8') == "end":
                            break
                    except Exception:
                        pass
                    f.write(data)
                    data = self.send_sock.recv(1024)
                f.close()

            # File deleted on server
            elif command.startswith('del:'):
                self.status = self.DELETING
                for filename in os.listdir(directory):
                    if FileTransfer.file_hash(directory + "\\" + filename) == command[4:]:
                        try:
                            print(self.status_color_mapping[self.status] + "Deleting file: " +
                                  Fore.LIGHTWHITE_EX + command[4:])
                            os.remove(directory+"\\"+command[4:])
                        except Exception:
                            pass
            # Hmmm?
            else:
                self.status = self.ERROR

            
con = Connection(config.PORT)
