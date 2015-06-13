__author__ = 'Liran & Rotem '
from RSAHandler import RSAHandler
from Crypto.PublicKey import RSA
import socket


PORT = 8888
HOST = ""
DST_IP = "127.0.0.1"


class Client(object):
    def __init__(self):
        self.sock = None
        self.my_rsa = RSAHandler()
        self.dst_public_key = None

    def open_connection(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    @staticmethod
    def send_message(socket_num, plain_message):
        socket_num.send(str(plain_message))

    def send_enc_message(self, socket_num, plain_message):
        Client.send_message(socket_num, RSAHandler.get_enc_message(plain_message, self.dst_public_key))

    def read_enc_message(self, source):
        return RSAHandler.get_dec_message(self.my_rsa.my_key, source)

    @staticmethod
    def read_plain_message(socket_num):
        return str(socket_num.recv(1024))

    def send_public_key(self, socket_num):
        print "Sending My Public Key"
        self.send_message(socket_num, self.my_rsa.public_key.exportKey())
        print "Key Sent"

    def read_public_key(self, socket_num):
        print "Reading Public Key"
        self.dst_public_key = RSA.importKey(self.read_plain_message(socket_num))
        print "I have a Public Key"


class Alice(Client):
    def __init__(self):
        super(Alice, self).__init__()
        self.dst_port = ""
        self.dst_ip = ""
        self.my_password = ""

    def open_connection(self):
        super(Alice, self).open_connection()
        self.sock.connect((self.dst_ip, self.dst_port))

    def set_dst_port_ip(self, port, ip):
        self.dst_ip = ip
        self.dst_port = port

    def password_request(self):
        print "Requesting Password..."
        self.send_enc_message(self.sock, "GET PWD")
        print "Waiting for password..."
        self.my_password = self.read_enc_message(self.sock.recv(1024))
        print "My Password is: " + self.my_password

    def password_re_set(self, new_password="random_password"):
        print "Setting New Password..."
        self.send_enc_message(self.sock, "SET PWD")
        if self.read_plain_message(self.sock) == "OK":
            print "Sending New Password..."
            self.send_enc_message(self.sock, new_password)

    def say_hey(self):
        print "Waving to Bob"
        self.send_message(self.sock, "Hey I'm Alice")
        self.read_plain_message(self.sock)
        print "Bob waved back"

    def send_public_key(self, socket_num=None):
        super(Alice, self).send_public_key(self.sock)

    def read_public_key(self, socket_num=None):
        self.send_message(self.sock, "GET PUBLIC KEY")
        super(Alice, self).read_public_key(self.sock)


class Bob(Client):
    def __init__(self):
        super(Bob, self).__init__()
        self.alice_password = "123456"

    def open_connection(self):
        super(Bob, self).open_connection()
        print "Binding..."
        self.sock.bind((HOST, PORT))
        print "Listening..."
        self.sock.listen(10)
        print "Accepting..."

        conn, address_info = self.sock.accept()
        print 'Connected with ' + address_info[0] + ':' + str(address_info[1]), "===================================="
        while True:
            data = conn.recv(1024)
            if not data:
                conn.close()
                return
            if data == "Hey I'm Alice":
                print "Waved To Alice"
                self.send_message(conn, "Hey I'm Bob")

            elif '-----BEGIN PUBLIC KEY-----' in data:
                print "Received Alice's Public Key"
                self.dst_public_key = RSA.importKey(str(data))

            elif "QUIT" == data:
                self.sock.close()
                break

            elif data == "GET PUBLIC KEY":
                print "Sent Alice My Public Key"
                self.send_public_key(conn)

            elif self.read_enc_message(data) == "GET PWD":
                print "Received GET PWD"
                self.send_enc_message(conn, self.alice_password)

            elif self.read_enc_message(data) == "SET PWD":
                print "Received SET PWD"
                self.send_message(conn, "OK")
                self.alice_password = self.read_enc_message(conn.recv(1024))
                print "Alice's password is: " + self.alice_password

            else:
                print "Other Data In: ", repr(data)


def client_alice():
    client = Alice()
    client.set_dst_port_ip(PORT, DST_IP)
    client.open_connection()
    client.say_hey()  # I'm Alice
    print("What You Can Do\n"
          "1.Send Public Key\n"
          "2.Read Public Key\n"
          "3.Get Password\n"
          "4.Set Password\n")
    while 1:
        data = raw_input("\nType Index or QUIT to Quit):")
        if data == "QUIT":
            client.send_message(client.sock, "QUIT")
            client.sock.close()
            break
        elif data == "1":
            client.send_public_key()
        elif data == "2":
            client.read_public_key()
        elif data == "3":
            client.password_request()
        elif data == "4":
            client.password_re_set()


def client_bob():
    client = Bob()
    client.open_connection()

raw_data = raw_input("Alice Or Bob:")

if raw_data == "Alice":
    client_alice()

elif raw_data == "Bob":
    client_bob()
