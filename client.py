import random
import hashlib
import base64
import time

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

import socket

from constants import HOST, PORT, NUM_PUZZLES, MAX_VALUE

class Puzzle:
    def __init__(self, num):
        self.x = num
        self.B1 = get_random_bytes(16)
        self.B2 = get_random_bytes(16)

        self.H1 = hashlib.sha256(self.x * self.B1).digest()
        self.H2 = hashlib.sha256(self.x * self.B2).digest()
    
    def format(self, formater):
        joiner = b'\x00'
        return self.B1 + joiner + self.H1 + joiner + self.B2

class ClientMerkle:
    def __init__(self, s:socket):
        ## Create connection
        self.s = s

        ## Generate puzzles
        puzzles = []                                                ## List of all puzzles
        identifiers = self.create_puzzles(puzzles)                  ## Maps H2 to puzzle

        ## Send puzzles
        for puzzle in puzzles:
            s.send(puzzle.format('utf-8'))
            time.sleep(0.001)

        s.send(b'\x00')
        print('SYSTEM: Puzzles Sent')
    
        ## Receive Response and Decode
        identifier = s.recv(1024)
        puzzle = identifiers[identifier]

        print(f"SYSTEM: Received Key")

        ## TODO: Set Key and Nonce
        key = puzzle.B2
        for i in range(puzzle.x):
            key = hashlib.sha256(key).digest()
        self.aes_key = key

        encryptor = AES.new(self.aes_key, AES.MODE_EAX)
        self.nonce = encryptor.nonce

        ## Send Over Nonce
        s.send(self.nonce)

    def create_puzzles(self, puzzles):
        identifiers = {}

        for i in range(NUM_PUZZLES):
            num_reps = random.randint(1, MAX_VALUE)
            new = Puzzle(num_reps)

            puzzles.append(new)
            identifiers[new.H2] = new

        return identifiers

    def recv(self, num):
        data = self.s.recv(num)
        return self.decrypt(data)
    
    def decrypt(self, data):
        decryptor = AES.new(self.aes_key, AES.MODE_EAX, self.nonce)
        return decryptor.decrypt(data).decode('utf-8')
    
    def send(self, data):
        msg = self.encrypt(data.encode('utf-8'))
        self.s.send(msg)
    
    def encrypt(self, data):
        encryptor = AES.new(self.aes_key, AES.MODE_EAX, self.nonce)
        return encryptor.encrypt(data)

if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        connection = ClientMerkle(s)
        print("___________________________________________________________________\n\n\n\n\n")

        text = input('Input: ')

        while text != None:
            connection.send(text)
            print("Recevied:", connection.recv(1024))

            text = input('Input: ')
