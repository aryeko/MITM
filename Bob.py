__author__ = 'Liran & Rotem '
from Client import Client
from Crypto.PublicKey import RSA


PORT = 8888
HOST = ""


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
        print 'Connected with ' + address_info[0] + ':' + str(address_info[1]), "\n===================================="
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
                self.rsa.dst_public_key = RSA.importKey(str(data))

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


# ================

client = Bob()
client.open_connection()
