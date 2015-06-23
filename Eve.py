__author__ = 'Liran & Rotem '
from Crypto.PublicKey import RSA
from threading import Thread
from Client import Client


LISTEN_PORT = 8886
CONNECTION_PORT = 8888
HOST = ""
DST_IP = "127.0.0.1"


class Eve:
    def __init__(self):
        self.Alice = Client()
        self.Alice.open_connection()

        self.Bob = Client()
        self.Bob.open_connection()

        self.Eve = Client()
        self.Eve.open_connection()

        self.alice_stolen_password = ""

    def wait_for_alice(self):
        print "Binding..."
        self.Eve.sock.bind((HOST, LISTEN_PORT))
        print "Listening..."
        self.Eve.sock.listen(10)
        print "Accepting..."
        conn, address_info = self.Eve.sock.accept()
        print 'Connected with ' + address_info[0] + ':' + str(address_info[1]), "\n===================================="
        th = Thread(target=self.start_communication_with_alice, args=(conn,))
        th.start()

    # ===== Pretending to be Alice =====

    def say_hello_to_bob(self):
        print "Waving to Bob"
        self.Bob.send_message(self.Bob.sock, "Hey I'm Alice")
        bob_response = self.Bob.read_plain_message(self.Bob.sock)
        print "Bob returns with ", bob_response
        return bob_response

    # ===== Pretending to be Bob =====
    def start_communication_with_alice(self, conn):
        '''
        :param conn: alice's socket
        :return:
        '''
        print "Alice Connected me, lets connect Bob..."
        self.Bob.sock.connect((DST_IP, CONNECTION_PORT))
        print "Connected with Bob"

        while True:
            print "==============================="
            data = conn.recv(1024)
            if not data:
                conn.close()
                return
            if data == "Hey I'm Alice":
                print "Alice Waved Me, lets wave bob..."
                bob_response = self.say_hello_to_bob()
                self.Alice.send_message(conn, bob_response)
                print "Waved to Alice"

            elif '-----BEGIN PUBLIC KEY-----' in data:
                print "Alice sent her public key\nStoring..."
                self.Alice.rsa.dst_public_key = RSA.importKey(str(data))
                print "Sending Bob Eve's public key"
                self.Eve.send_public_key(self.Bob.sock)
                print "Sent bob EVE's public key"

            elif "QUIT" == data:
                self.Eve.send_message(self.Bob.sock, "QUIT")
                self.Bob.sock.close()
                conn.close()
                print "Eve is quitting..."
                break

            elif data == "GET PUBLIC KEY":
                print "Getting Public key from Bob..."
                self.Eve.send_message(self.Bob.sock, "GET PUBLIC KEY")
                self.Bob.read_public_key(self.Bob.sock)
                print "Sending Alice our public key..."
                self.Eve.send_public_key(conn)
                print "Done"

            elif self.Eve.read_enc_message(data) == "GET PWD":
                print "Alice has requested for password, lets ask Bob for it first..."
                self.Bob.send_enc_message(self.Bob.sock, "GET PWD")
                print "Waiting for Bob's response..."
                self.alice_stolen_password = self.Eve.read_enc_message(self.Bob.sock.recv(1024))
                print "I've got the password from Bob: " + self.alice_stolen_password

                # print "Lets send Alice's a changed version of the password"
                # changed_version_of_password = raw_input("Type in a password to foll Alice")
                # self.Alice.send_enc_message(conn, changed_version_of_password)

                self.Alice.send_enc_message(conn, self.alice_stolen_password)

            elif self.Eve.read_enc_message(data) == "SET PWD":
                print "Alice has requested to change password, lets change the password"
                self.Bob.send_enc_message(self.Bob.sock, "SET PWD")
                if self.Bob.read_plain_message(self.Bob.sock) == "OK":
                    self.Alice.send_message(conn, "OK")
                    self.alice_stolen_password = self.Eve.read_enc_message(conn.recv(1024))
                    print "Alice changed her password to " + self.alice_stolen_password
                    print "Sending Bob alice's new password"
                    self.Bob.send_enc_message(self.Bob.sock, self.alice_stolen_password)

            else:
                print "Other Data In: ", repr(data)
                pass
                # we have different command. we will print it or pass it
            print "==============================="


eve = Eve()
eve.wait_for_alice()
