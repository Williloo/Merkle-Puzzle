import socket
import random
import hashlib

import sys

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from constants import PORT, NUM_PUZZLES, MAX_VALUE

HOST = ''

class ServerMerkle:
    def __init__(self, conn):
        ## Initiate Connection
        self.conn = conn

        ## Receive Puzzles
        puzzles = []
        while True:
            data = conn.recv(1024)
            if data == b'\x00':
                break
            puzzles.append(data.split(b'\x00'))

        print('    MERKLE: Puzzles Received')

        ## Pick Random Puzzle
        i = random.randint(0, NUM_PUZZLES - 1)
        while i >= len(puzzles):
            i = random.randint(0, NUM_PUZZLES - 1)
        
        ## Decrypt Puzzle
        B1, H1, B2, *_ = puzzles[i]

        print('    MERKLE: Decrypting')
        x = self.merkle_decrypt(B1, H1)
        print('    MERKLE: Decrypted')

        ## Send Back H2
        self.conn.send(hashlib.sha256(x * B2).digest())
        print("    MERKLE: Key Sent")

        ## Set Key
        key = B2

        for i in range(x):
            key = hashlib.sha256(key).digest()
        self.aes_key = key

        ## Receive and set nonce
        self.nonce = conn.recv(1024)
        print("    MERKLE: Nonce Received")

    def progress_bar(self, current, total, bar_length=20):
        fraction = current / total

        arrow = int(fraction * bar_length - 1) * '-' + '>'
        padding = int(bar_length - len(arrow)) * ' '

        ending = '\r' if current == total else '\r'

        sys.stdout.write(ending+f'        Progress: [{arrow}{padding}] {int(fraction*100)}%')

    def merkle_decrypt(self, B1, H1):
        attempt = B1
        count = 1

        while (hashlib.sha256(attempt).digest() != H1):
            self.progress_bar(count, MAX_VALUE)
            attempt += B1
            count += 1
        
        print('\n')
        
        return count

    def recv(self, num):
        data = self.conn.recv(num)
        return self.decrypt(data)
    
    def decrypt(self, data):
        decryptor = AES.new(self.aes_key, AES.MODE_EAX, self.nonce)
        return decryptor.decrypt(data).decode('utf-8')
    
    def send(self, data):
        msg = self.encrypt(data.encode('utf-8'))
        self.conn.send(msg)
    
    def encrypt(self, data):
        encryptor = AES.new(self.aes_key, AES.MODE_EAX, self.nonce)
        return encryptor.encrypt(data)

if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))

        while True:
            s.listen()
            conn, addr = s.accept()
            with conn:
                print('SYSTEM: Connected by', addr)

                print("SYSTEM: Initiate Merkle")
                connection = ServerMerkle(conn)
                print("SYSTEM: Complete Merkle")

                while True:
                    data = connection.recv(1024)

                    if not data:
                        print("SYSTEM: Disconnected by", addr)
                        break
                        
                    print(addr, ': ', data)

                    connection.send(data)
