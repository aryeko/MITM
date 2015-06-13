__author__ = 'Liran & Rotem '
import socket
import sys
import thread
from Crypto.PublicKey import RSA
from RSAHandler import RSAHandler

class ClientToFool:
    def __init__(self):
        self.sock = None
        self.key = None
        self.last_message = None

    @property
    def sock(self):
        return self.sock

    @property
    def key(self):
        return self.key

    @property
    def last_message(self):
        return self.last_message

    @sock.setter
    def sock(self, sock):
        self.sock = sock

    @key.setter
    def key(self, key):
        self.key = key

    @last_message.setter
    def last_message(self, last_message):
        self.last_message = last_message


class Server:
    def __init__(self):
        self.socket = None
        self.host = ''
        self.port = 8888

        self.Alice = ClientToFool()
        self.Bob = ClientToFool()

    def start_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print "Eve Socket is Created"
        try:
            self.socket.bind((self.host, self.port))
        except socket.error as msg:
            print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            sys.exit()
        print "Eve Socket is Bind"

        self.socket.listen(10)
        print "Eve Socket is now Listening..."
        while True:
            conn, address_info = self.socket.accept()
            print 'Connected with ' + address_info[0] + ':' + str(address_info[1])
            thread.start_new_thread(self.client_thread, (conn,))
        self.socket.close()

    def client_thread(self, conn):
        #  infinite loop so that function do not terminate and thread do not end.
        while True:
            if self.Bob.sock is None or self.Alice.sock is None:
                data = conn.recv(1024)
            else:
                conn.close()
                break
            if not data:
                conn.close()
                break
            else:
                if 'Alice' in data:
                    self.Alice.sock = conn
                    thread.start_new_thread(self.start_with_alice, ())
                    break
                elif 'Bob' in data:
                    self.Bob.sock = conn
                    thread.start_new_thread(self.start_with_bob, ())
                    break

    def start_with_bob(self):
        while True:
            data = self.Bob.sock.recv(1024)
            if '-----BEGIN PUBLIC KEY-----' in data:
                self.Bob.key = RSA.importKey(str(data))
                send_data = RSAHandler.get_enc_message("Thanks For The Key", self.Bob.key)
                self.Bob.sock.send(send_data)

            elif data == "QUIT":
                print "Bob is out"
                break
            if not data:
                break

        self.Bob.sock.close()

    def start_with_alice(self):
        while True:
            data = self.Alice.sock.recv(1024)
            if '-----BEGIN PUBLIC KEY-----' in data:
                self.Alice.key = RSA.importKey(str(data))
                send_data = RSAHandler.get_enc_message("Thanks For The Key", self.Alice.key)
                self.Alice.sock.send(send_data)

            elif data == "QUIT":
                print "Bob is out"
                break
            if not data:
                break
        self.Alice.sock.close()


serv = Server()
serv.start_server()
