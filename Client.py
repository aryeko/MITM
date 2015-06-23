__author__ = 'Liran & Rotem '
from RSAHandler import RSAHandler
from Crypto.PublicKey import RSA
import socket


PORT = 8888
HOST = ""
DST_IP = "10.0.0.3"


class Client(object):
    def __init__(self):
        self.sock = None
        self.rsa = RSAHandler()

    def open_connection(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    @staticmethod
    def send_message(socket_num, plain_message):
        socket_num.send(str(plain_message))

    def send_enc_message(self, socket_num, plain_message):
        Client.send_message(socket_num, RSAHandler.get_enc_message(plain_message, self.rsa.dst_public_key))

    def read_enc_message(self, source):
        return RSAHandler.get_dec_message(self.rsa.my_key, source)

    @staticmethod
    def read_plain_message(socket_num):
        return str(socket_num.recv(1024))

    def send_public_key(self, socket_num):
        print "Sending My Public Key"
        self.send_message(socket_num, self.rsa.public_key.exportKey())
        print "Key Sent"

    def read_public_key(self, socket_num):
        print "Reading Public Key"
        self.rsa.dst_public_key = RSA.importKey(self.read_plain_message(socket_num))
        print "I have a Public Key"
