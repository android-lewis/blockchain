import blockchain
from miner_config import MINER_ADDRESS, MINER_NODE_URL
import ecdsa
import base64
from uuid import uuid4
from flask import Flask, jsonify, request

# Setup a few variables
MINING_REWARD = 50

# Flask setup
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Create an address for node on Port 5000
node_address = str(uuid4()).replace('-', '')

# Create an instance of Blockchain
chain = blockchain.Blockchain()

# Set up our API routes

# Mine a new block
@app.route('/mine', methods = ['GET'])
def mine_block():
    previous_block = chain.get_previous_block()
    previous_proof = previous_block['proof']
    new_proof = chain.proof_of_work(previous_proof)
    previous_hash = chain.hash(previous_block)

    # Add a new transaction to reward the miner
    chain.add_transaction(sender = node_address, reciever= MINER_ADDRESS, amount= MINING_REWARD)
    new_block = chain.create_block(new_proof, previous_hash)
    response = {
        'message': 'Block mined', 
        'index': new_block['index'],
        'timestamp': new_block['timestamp'],
        'proof': new_block['proof'],
        'previous_hash': new_block['previous_hash'],
        'transactions': new_block['transactions']
    }
    return jsonify(response), 200

# Return the entire chain
@app.route('/view_chain', methods = ['GET'])
def view_chain():
    response = {'chain': chain.chain, 
                'length': len(chain.chain) }
    return response, 200

# Validate the current chain
@app.route('/validate_chain', methods = ['GET'])
def validate():
    is_valid = chain.validate_chain(chain.chain)
    if is_valid :
        return {'message' : 'All good, the chain is valid'}
    else:   
        return {'message' : 'There is a problem, the chain is not valid'}

# Add a new transaction       
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    new_txion = request.get_json()
    transaction_keys = ['sender', 'reciever', 'amount', 'signature', 'message']
    if not all (keys in new_txion for keys in transaction_keys):
        return 'Malformed request: please include sender, reciever and amound', 400
    else:
        if validate_signature(new_txion['sender'], new_txion['signature'], new_txion['message']):
            index = chain.add_transaction(sender = new_txion['sender'], reciever = new_txion['reciever'], amount = new_txion['amount'])
            response = {'message': f'This transaction will be added at block index {index}'}
            return jsonify(response), 201
        else:
            return "Transaction submission failed. Wrong signature\n", 400

def validate_signature(public_key, signature, message):
    """Verifies if the signature is correct. This is used to prove
    it's you (and not someone else) trying to do a transaction with your
    address. Called when a user tries to submit a new transaction.
    """
    public_key = (base64.b64decode(public_key)).hex()
    signature = base64.b64decode(signature)
    vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(public_key), curve=ecdsa.SECP256k1)
    
    # Try changing into an if/else statement as except is too broad.
    try:
        return vk.verify(signature, message.encode())
    except:
        return False

# Connect a new node
@app.route('/connect', methods=['POST'])
def connect_node():
    json = request.get_json()
    node_list = json.get('nodes')
    if node_list is None:
        return "No nodes", 400
    else:
        for node in node_list:
            chain.add_node(node)
    
    response = {
        'message': 'All nodes now connected', 
        'total_nodes': list(chain.nodes)
        } 
    
    return response, 201

# Update the chain if needed
@app.route('/update_chain', methods=['GET'])
def update_chain():
    is_longest = chain.replace_chain()
    if is_longest :
        response = {'message' : 'The chain was updated', 'new_chain': chain.chain}
    else:   
        response = {'message' : 'Chain up to date', 'current_chain': chain.chain}

    return response, 200

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.0.1', port=port)
