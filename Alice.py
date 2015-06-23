__author__ = 'Liran & Rotem '
from Client import Client


PORT = 8886
HOST = ""
DST_IP = "127.0.0.1"


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

    def password_re_set(self, new_password):
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
            new_password = raw_input("\nType A New Password:")
            client.password_re_set(new_password)

# ================

client_alice()
