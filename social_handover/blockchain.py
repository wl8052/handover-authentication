# 这里建立区块链，并在区块链中上传上最初的节点位置信息和初始节点社交关系

import hashlib
import random
from datetime import datetime, timedelta
from random import randint
import time
import json

import numpy as np
from flask import Flask, jsonify, request
import math


class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.new_block(previous_hash='1', proof=100)

    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.mktime(time.gmtime()),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, node1, node2, interaction_time):
        self.current_transactions.append({
            'node1': node1,
            'node2': node2,
            'interaction_time': interaction_time,
            'type': 'interaction'
        })
        self.new_block(previous_hash=self.hash(self.chain[-1]), proof=100)  # 添加这行代码来立即将交易添加到区块链
        return self.last_block['index']


    def add_nodes(self, nodes):
        for node in nodes:
            self.current_transactions.append({
                'node_name': node['node_name'],
                'x': node['x'],
                'y': node['y'],
                'type': 'node'
            })
        self.new_block(previous_hash=self.hash(self.chain[-1]), proof=100)


    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()


app = Flask(__name__)
blockchain = Blockchain()


@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    values = request.get_json()
    required = ['node1', 'node2', 'interaction_time']
    if not all(k in values for k in required):
        return 'Missing values', 400
    index = blockchain.new_transaction(values['node1'], values['node2'], values['interaction_time'])
    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/nodes', methods=['GET'])       # 节点位置信息http://localhost:5000/nodes
def get_nodes():
    nodes = []
    for block in blockchain.chain:
        for transaction in block['transactions']:
            if transaction['type'] == 'node':
                nodes.append({'node_name': transaction['node_name'], 'x': transaction['x'], 'y': transaction['y']})
    return jsonify(nodes), 200


@app.route('/interactions', methods=['GET'])  # http://localhost:5000/interactions
def get_interactions():
    interactions = []
    for block in blockchain.chain:
        for transaction in block['transactions']:
            if transaction['type'] == 'interaction':
                interactions.append({'node1': transaction['node1'], 'node2': transaction['node2'], 'interaction_time': transaction['interaction_time']})
    return jsonify(interactions), 200


def calculate_distance(node1, node2):
    return math.sqrt((node1['x'] - node2['x'])**2 + (node1['y'] - node2['y'])**2)

if __name__ == '__main__':
    nodes = []
    for i in range(1, 1000):
        node_location_x = round(random.uniform(0, 15), 2)  # 随机生成范围在0到15之间的小数
        node_location_y = round(random.uniform(0, 15), 2)
        one_node = {'node_name': i, 'x': node_location_x, 'y': node_location_y}
        blockchain.add_nodes([one_node])
        nodes.append(one_node)

    for i in range(len(nodes)):
        for j in range(i+1, len(nodes)):
            distance = calculate_distance(nodes[i], nodes[j])
            is_empty = random.randint(1, 3) == 1
            if is_empty:
                days = randint(3, 7)
                hours = randint(0, 23)
                minutes = randint(0, 59)
                seconds = randint(0, 59)
            else:
                days = randint(0, 3)
                hours = randint(0, 23)
                minutes = randint(0, 59)
                seconds = randint(0, 59)
            if distance <= 1:
                interaction_time = datetime.now() - timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
                interaction_time_str = interaction_time.strftime('%Y-%m-%d %H:%M:%S')
                transaction = {'node1': nodes[i]['node_name'], 'node2': nodes[j]['node_name'], 'interaction_time': interaction_time_str}
                blockchain.new_transaction(nodes[i]['node_name'], nodes[j]['node_name'], interaction_time_str)
    app.run(host='0.0.0.0', port=5000)

