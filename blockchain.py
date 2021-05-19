import datetime
import hashlib
import json
import requests
from urllib.parse import urlparse

# Blockchain class
class Blockchain:

    # Contructor
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.create_block(proof = 1, prev_hash = '0')
        self.nodes = set()

    def create_block(self, proof, prev_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': prev_hash,
            'transactions': self.pending_transactions 
            }
        self.pending_transactions = []
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        nonce = 1
        check_proof = False

        while check_proof is False :
            # Operation needs to be non symmetrical
            hash_operation = hashlib.sha256(str(nonce**64 - previous_proof**32).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                nonce += 1
        return nonce

    def hash(self, block):
        # Encode block keys in JSON format and encode for SHA256
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    # Check that our block chain is valid
    def validate_chain(self, chain):
        block_index = 1
        previous_block = chain[0]
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**64 - previous_proof**32).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True

    # Add a new transaction to a new block
    def add_transaction(self, sender, reciever, amount):
        self.pending_transactions.append({
            'sender': sender,
            'reciever': reciever,
            'amount': amount
        })

        previous_block = self.get_previous_block()
        return previous_block['index'] + 1

    # Add a non relative address (url + port) of our new node to the node set
    def add_node(self, address):
        node_address = urlparse(address)
        self.nodes.add(node_address.netloc)

    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)

        for nodes in network:
            response = requests.get(f'http://{nodes}/view_chain')
            if response.status_code == 200:
                length = response.json()['length']
                new_chain = response.json()['chain']
                if length > max_length and self.validate_chain(new_chain):
                    max_length = length
                    longest_chain = new_chain
        
        if longest_chain:
            self.chain = longest_chain
            return True
        return False
