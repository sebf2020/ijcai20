# This code uses three types of token data
# an oracle group machine need to be added（The source code will be released in the next step）
# In order to facilitate deployment, we used local txt instead of database and use light flask http

import hashlib
import json
import uuid
from argparse import ArgumentParser
from time import time, sleep
from urllib.parse import urlparse
import requests
from flask import Flask, jsonify
from flask import request
from time import sleep

class Blockchain(object):
    # Initialize parameters and create a genesis block. The blockchain stores all previous chains and currently collected transaction data
    def __init__(self):
        self.chain=[]
        self.current_transactions=[]
        self.nodes=set()
        self.merkletree=0
        # Creation block establishment
        self.new_block(100,1)
        self.ttype = []

    def register_node(self,node):
        address=urlparse(node)
        self.nodes.add(address.netloc)

    # To verify whether the neighbor node block is true, it is necessary to verify whether the previous_hash is equal to the hash of the previous block, and whether the proof meets the condition that the first n is 0
    def vaild_chain(self,chain):
        n=0
        previous_block=chain[n]
        later_block=chain[n+1]
        while n+1<len(chain):
            if later_block['previous_hash']!=self.hash(previous_block):
                print('hash compare fail')
                return False
            # vaild_proof_of_work (proof of the next block, merkle of the next block, previous_hash of the current block)
            if not self.vaild_proof_of_work(later_block['proof'], later_block['merkle'],later_block['previous_hash']):
                print(later_block['proof'])
                print(later_block['merkle'])
                print(later_block['previous_hash'])
                print('proof compare fail')
                return False
            n+=1
        return True

    def resolve_conflict(self):
        self_length=len(self.chain)
        neighbour=self.nodes
        new_blcok=None

        # Traverse neighbor nodes
        for node in neighbour:
            # Get chain information from neighbor nodes, requests('url')
            url='http://%s/chain'%node
            print(url)
            response= requests.get(url)
            # Receive data
            if response.status_code==200:
                length=response.json()['length']
                chain=response.json()['chain']
                print('staatus_code is ok')
            # Determine whether the chain is the longest chain, if not, it will be replaced
                if self_length<length and self.vaild_chain(chain):
                    self_length=length
                    new_blcok=chain
                    print('compare ok')
        # If a replacement has occurred
        if new_blcok:
            self.chain=new_blcok
            print('exchange ok')
            return True

        return  False

    # Define the structure of the block ------------------------(block header + block body)------------ ----------------
    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.last_block),
            'transactions': self.current_transactions,
            'merkle':self.merkletree
        }
        self.current_transactions = []
        self.chain.append(block)
        return block

    # Collect transaction function ----------------------------------(block body)------- ------------------------
    def dsrc(self, ttype, sender, recipient, mtype, hmsg, communtype):
        self.current_transactions.append(
            {
                'T-Type': ttype,
                'Sender': sender,
                'Receiver': recipient,
                'M-Type': mtype,
                'Msg': hmsg,
                'Communication object': communtype
            }
        )
        # Mark the block to which the transaction belongs
        return self.last_block['index']+1

    def fees(self, ttype, sender, recipient, mtype, hmsg, fees):
        self.current_transactions.append(
            {
                'T-Type': ttype,
                'Sender': sender,
                'Receiver': recipient,
                'M-Type': mtype,
                'Msg': hmsg,
                'Fees': fees
            }
        )
        # Mark the block to which the transaction belongs
        return self.last_block['index']+1

    def traffic_vio(self, ttype, sender, recipient, license_plate):
        self.current_transactions.append(
            {
                'T-Type': ttype,
                'Sender': sender,
                'Receiver': recipient,
                'License plate': license_plate
            }
        )
        # Mark the block to which the transaction belongs
        return self.last_block['index']+1


    # Return to the last block
    @property
    def last_block(self):
        return self.chain[-1]

    # sha256
    @staticmethod
    def hash(block):
        json_string=json.dumps(block,sort_keys=True).encode()
        return hashlib.sha256(json_string).hexdigest()

    # Pow
    def proof_of_work(self):
        proof_randnum=0
        previous_hash=self.hash(self.last_block)
        while self.vaild_proof_of_work(proof_randnum,self.merkletree,previous_hash) is False:
            proof_randnum+=1
        return proof_randnum

    # Repeatedly calculate the hash value that meets the requirements and the first four bits are 0
    def vaild_proof_of_work(self,proof_randnum,merkle,previous_hash)->bool:
        hash_string='%s%s%s'%(proof_randnum,merkle,previous_hash)
        hash_string=hash_string.encode()
        guess_num=hashlib.sha256(hash_string).hexdigest()
        if guess_num[0:4] == '0000':
            print('block proof:',proof_randnum)
            return True
        else:
            return False

    # Add non-repeated checktype
    def count_ttype_num(self,unsort_type):
        if unsort_type not in self.ttype:
            self.ttype.append(unsort_type)

    # Define empty lists of different ttypes and use them in mine
    def make_ttype_list(self):
        for sort_type in self.ttype:
            exec('self.ttypelist{}= []'.format(sort_type))
            # Make a hash copy of ttype to store the hash value of ttypelist
            exec('self.hash_ttypelist{} = []'.format(sort_type))


    # Add all the data belonging to the ttype in current_transactions to the subtree
    def arrange_ttype_list(self):
        for sort_tran in self.current_transactions:
            for check_ttype in self.ttype:
                # for loop to take dict element from list
                if check_ttype == sort_tran['T-Type']:
                    # The original transaction is added to the self.ttypelist xxxx array
                    exec('self.ttypelist'+'%s.append(sort_tran)' % check_ttype)
                    # The original transaction hash is added to self.hash_ttypelist xxxx
                    t = self.merkle_hash_1(sort_tran)
                    exec('self.hash_ttypelist' + '%s.append(t)' % check_ttype)

    def merkle_hash_1(self,data):
        json_string = json.dumps(data,sort_keys=True).encode()
        return hashlib.sha256(json_string).hexdigest()

    def merkle_hash_2(self,data1,data2):
        data = '%s%s' % (data1, data2)
        json_string = json.dumps(data,sort_keys=True).encode()
        return hashlib.sha256(json_string).hexdigest()

    def inside_merkle(self):
        # 统计merkle执行时间
        startTimeStamp = time()
        self.make_ttype_list()
        self.arrange_ttype_list()
        for cur_ttype in self.ttype:
            self.currentttype = cur_ttype
            # self.temp_leaf points to the address of transactions such as self.ttypelistdsrc
            exec('self.temp_leaf = self.ttypelist{}'.format(cur_ttype))
            # Create a dynamic file name to save the original transaction data
            exec("self.file = open('{}transaction.txt','w')".format(cur_ttype))
            self.file.write(str(self.temp_leaf) + '\n')
            self.file.close()
            # self.temp_hash points to copy addresses such as self.hash_ttypelist
            exec('self.temp_hash = self.hash_ttypelist{}'.format(cur_ttype))
            # Calculate the root hash of the subtree
            self.make_leaf_root()
            # Add the elements of the last length 1 list in temp_hash to the subtree root list
            print(cur_ttype)
            if(len(self.temp_hash) == 0):
                break
            print('sub_tree hash is',self.temp_hash)
            self.root_list.append(self.temp_hash[0])
        # The next thing to do is to call the root of each subtree merkle root (the default is an even number, fill in the blanks and do it later)
        print(self.root_list)
        self.make_merkle_root()
        self.merkletree = self.root_list[0]
        self.file = open('root.txt', 'a')
        self.file.write(str(self.root_list) + '\n')
        self.file.close()
        print('merkle tree root is %s' % self.merkletree)
        endTimeStamp = time()
        print('make tree time:',endTimeStamp - startTimeStamp)

    # Calculate the Merkel root of the subtree
    def make_leaf_root(self):
        # Fill in the blank binary position
        if len(self.temp_hash) % 2 == 1:
            self.temp_hash.append('ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff')
        while len(self.temp_hash) > 1:
            # Fill in the blank binary position
            if len(self.temp_hash) % 2 == 1:
                self.temp_hash.append('ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff')
            length = len(self.temp_hash)
            i = 0
            j = 1
            n = 0
            print('temp hash is %s' % self.temp_hash)
            # Subtree hash value record
            exec("self.file = open('{}transaction.txt','a')".format(self.currentttype))
            self.file.write(str(self.temp_hash) + '\n')
            self.file.close()
            while i != length:
                t = self.merkle_hash_2(self.temp_hash[i],self.temp_hash[j])
                self.temp_hash[n] = t
                i = i + 2
                j = j + 2
                n = n + 1
            # list fragmentation
            self.temp_hash = self.temp_hash[0:length//2]

    def make_merkle_root(self):
        # Reset root.txt
        self.file = open('root.txt', 'w')
        self.file.close()
        if len(self.root_list) % 2 == 1:
            self.root_list.append('ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff')
            print('root list is %s' % self.root_list)
        while len(self.root_list) > 1:
            if len(self.root_list) % 2 == 1:
                self.root_list.append('ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff')
            length = len(self.root_list)
            i = 0
            j = 1
            n = 0
            # The root of each subtree is written to root.txt
            self.file = open('root.txt', 'a')
            self.file.write(str(self.root_list) + '\n')
            self.file.close()
            while i != length:
                t = self.merkle_hash_2(self.root_list[i],self.root_list[j])
                self.root_list[n] = t
                i = i + 2
                j = j + 2
                n = n + 1
            self.root_list = self.root_list[0:length//2]

    # Import external data and generate Merkel tree
    def merkle(self,oracle_data_list):
        self.temp_leaf = []
        self.temp_hash = []
        self.root_list = []
        #Add external oracles and data to the subtree root set
        oracle_hash_list = []
        for data in oracle_data_list:
            oracle_hash_list.append(self.merkle_hash_1(data))
        self.temp_hash = oracle_hash_list
        self.make_leaf_root()
        self.root_list.append(self.temp_hash[0])
        #token type make root
        self.inside_merkle()


def hash_1(data):
    json_string = json.dumps(data,sort_keys=True).encode()
    return hashlib.sha256(json_string).hexdigest()

def hash_2(data1, data2):
    data = '%s%s' % (data1, data2)
    json_string = json.dumps(data, sort_keys=True).encode()
    return hashlib.sha256(json_string).hexdigest()

def readtxt1(check_ttype,light_node_data):
    if check_ttype != 'dsrc':
        print('error input')
        return [],[]
    f = open('dsrctransaction.txt')
    core_hash = []
    neighbour_hash = []
    line_list = []
    line = f.readline()
    light_node_hash = hash_1(light_node_data)
    line = f.readline()
    i = 0
    line_list.append('')
    for temp in line:
        if temp == '[' or temp == ']' or temp == "'" or temp == " " or temp == "\n":
            continue
        if temp == ',':
            line_list.append('')
            i = i + 1
            continue
        line_list[i] = line_list[i] + str(temp)
    flag = False
    count = 0
    line_count = 0
    for first_line_hash in line_list:
        if first_line_hash == light_node_hash:
            flag = True
            line_count = count
            break
        count = count + 1
    if flag == True:
        print('data has been saving')
    else:
        print('can not find data')
        return [],[]
    while line:
        line_list = []
        i = 0
        line_list.append('')
        for temp in line:
            if temp == '[' or temp == ']' or temp == "'" or temp == " " or temp == "\n":
                continue
            if temp == ',':
                line_list.append('')
                i = i + 1
                continue
            line_list[i] = line_list[i] + str(temp)
        print(line_list)
        print(line_count)
        if line_count % 2 == 0:
            core_hash.append(line_list[line_count])
            neighbour_hash.append(line_list[line_count + 1])
        else:
            core_hash.append(line_list[line_count])
            neighbour_hash.append(line_list[line_count - 1])
        line = f.readline()
        line_count = line_count // 2
    f.close()
    f = open('root.txt')
    line = f.readline()
    line_list = []
    i = 0
    line_list.append('')
    for temp in line:
        if temp == '[' or temp == ']' or temp == "'" or temp == " " or temp == "\n":
            continue
        if temp == ',':
            line_list.append('')
            i = i + 1
            continue
        line_list[i] = line_list[i] + str(temp)

    flag = False
    count = 0
    line_count = 0
    for temps in line_list:
        if temps == hash_2(core_hash[-1], neighbour_hash[-1]) or temps == hash_2(neighbour_hash[-1],core_hash[-1]):
            flag = True
            # line_count is responsible for recording the index value of the number of cores that need to be saved for each line
            line_count = count
            break
        count = count + 1
    if flag == True:
        print('ROOTdata has been saving')
    else:
        print('can not find data')
        return [], []

    while line:
        line_list = []
        i = 0
        line_list.append('')
        for temp in line:
            if temp == '[' or temp == ']' or temp == "'" or temp == " " or temp == "\n":
                continue
            if temp == ',':
                line_list.append('')
                i = i + 1
                continue
            line_list[i] = line_list[i] + str(temp)
        # Stop when reading to the root
        if len(line_list) == 1:
            core_hash.append(line_list[line_count])
            break
        if line_count % 2 == 0:
            core_hash.append(line_list[line_count])
            neighbour_hash.append(line_list[line_count + 1])
        else:
            core_hash.append(line_list[line_count])
            neighbour_hash.append(line_list[line_count - 1])
        line_count = line_count // 2
        line = f.readline()
    f.close()
    return core_hash,neighbour_hash


blockchain = Blockchain()
# Whether to access the oracle when mining
oracle_flag = False
# Generate random identification codes based on gateways, etc.
miner_self_identity=str(uuid.uuid4()).replace('-', '')
app = Flask(__name__)

@app.route('/help',methods=['GET'])
def blockchain_help():
    response = {
        "help01": "How to get newest block chain",
        "01methods": "GET",
        "01url input": "/chain",
        "---------------": "----------------------",
        "help02": "How to add a new transaction",
        "02methods": "POST",
        "02url input": "/transactions/new",
        "02body options": "raw-json",
        "02body model": "{sender,recipient,amount}"
    }
    return jsonify(response),200

res_dict = []

# Define receiving and receiving transaction routing
@app.route('/transactions/new', methods=['POST'])
def transactions():
    values = request.get_json()
    checktype = ''
    if 'T-Type' in values:
        checktype = values['T-Type']
        blockchain.count_ttype_num(checktype)
    # Record how many T-Types there are
    if checktype == 'dsrc':
        check = ['T-Type', 'Sender', 'Receiver', 'M-Type', 'Msg', 'Communication object']
        # Check data integrity
        if values is None:
            return 'Error:No Data input', 400
        if not all(k in check for k in values):
            return 'Missing Data input', 400
        # Corresponding location of write block
        index=blockchain.dsrc(values['T-Type'], values['Sender'], values['Receiver'], values['M-Type'], values['Msg'], values['Communication object'])
        response = 'We will add this transactions to block%s' % index
        return jsonify(response),201

    elif checktype == 'fees':
        check = ['T-Type', 'Sender', 'Receiver', 'M-Type', 'Msg', 'Fees']
        if values is None:
            return 'Error:No Data input', 400
        if not all(k in check for k in values):
            return 'Missing Data input', 400
        index=blockchain.fees(values['T-Type'], values['Sender'], values['Receiver'], values['M-Type'], values['Msg'], values['Fees'])
        response = 'We will add this transactions to block%s' % index
        return jsonify(response),201

    elif checktype == 'trafficvio':
        check = ['T-Type', 'Sender', 'Receiver', 'License plate']
        if values is None:
            return 'Error:No Data input', 400
        if not all(k in check for k in values):
            return 'Missing Data input', 400
        index=blockchain.traffic_vio(values['T-Type'], values['Sender'], values['Receiver'], values['License plate'])
        response = 'We will add this transactions to block%s' % index
        return jsonify(response),201
    # If it is not token, send it to the oracle for inquiry
    else:
        global oracle_flag
        oracle_flag = True
        headers = {'content-type': 'application/json'}
        rsuurl = 'http://127.0.0.1:8000/confirm_data'
        res = requests.post(url=rsuurl, data=json.dumps(values), headers=headers)
        # Add extend tx to local block
        temp_data = json.load(res.text)
        res_dict.append(temp_data)
        return 'transaction has been added to blockchain', 201


# Define the route that returns the content of the current block
@app.route('/chain', methods=['GET'])
def chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response),200

#mine
@app.route('/mine', methods=['GET'])
def mine():
    global oracle_flag
    global res_dict
    if oracle_flag == True:
        blockchain.merkle(res_dict)
        res_dict = []
    # 生成merkle树
    else:
        res_dict = []
        blockchain.merkle(res_dict)
    proof = blockchain.proof_of_work()
    current_block= blockchain.new_block(proof, previous_hash=None)
    respone = {
        'message': 'A new block has been mined',
        'index': current_block['index'],
        'timestamp': current_block['timestamp'],
        'proof': current_block['proof'],
        'previous_hash': current_block['previous_hash'],
        'transactions': current_block['transactions'],
        'merkle': current_block['merkle'],
        'blcok_total_length': len(blockchain.chain)
    }
    blockchain.ttype = []
    return jsonify(respone),200

# node register
@app.route('/node/register',methods=['POST'])
def node_register():
    values = request.get_json()
    if values is None:
        return 'None data input',400
    nodes = values.get('nodes')
    for node in nodes:
        blockchain.register_node(node)
    response={
        "message":"nodes add successfully",
        "total nodes":list(blockchain.nodes)
    }
    return jsonify(response),201

# Blockchain conflict resolution
@app.route('/conflict/resolve',methods=['GET'])
def conflict_resolve():
    oldindex = blockchain.last_block['index']
    judgement = blockchain.resolve_conflict()
    if judgement is False:
        response = {
            "message": "we are the right chain",
            "old_index": oldindex,
            "newest_index": blockchain.last_block['index']
        }
    else:
        response={
            "message": "we have replaced newest chain",
            "old_index": oldindex,
            "newest_index": blockchain.last_block['index']
        }
    return jsonify(response), 200

@app.route('/transaction/check1',methods=['POST'])
def transaction_check1():
    values = request.get_json()
    checktype = values['T-Type']
    if values is None:
        return 'None data input',400
    core_list,neighbour_list = readtxt1(checktype, values)
    response = {
        "core_list":core_list,
        "neighbour_list":neighbour_list
    }

    return jsonify(response),200


if __name__=='__main__':
    parser=ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, help='input your using port')
    args=parser.parse_args()
    port=args.port

    app.run(host='0.0.0.0', port=port, debug=True)
