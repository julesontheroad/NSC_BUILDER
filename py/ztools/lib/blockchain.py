import sys
import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4
import os
import Config
import Nsps
import Fs
import File
import Type
import Keys
import Hex
from binascii import hexlify as hx, unhexlify as uhx

import requests
from flask import Flask, jsonify, request


class KeyEntry:
	def __init__(self, titleId = None, titleKey = None, ncaHeader = None, sectionHeaderBlock = None, pfs0Header = None, pfs0Offset = None, json = None):
		self.titleId = titleId
		self.titleKey = titleKey
		self.ncaHeader = ncaHeader
		self.sectionHeaderBlock = sectionHeaderBlock
		self.pfs0Header = pfs0Header
		self.pfs0Offset = pfs0Offset

		if json:
			self.deserialize(json)

	def verify(self):
		ncaHeader = Fs.NcaHeader()
		ncaHeader.open(File.MemoryFile(self.ncaHeader, Type.Crypto.XTS, uhx(Keys.get('header_key'))))

		id = ncaHeader.rightsId[0:16].decode().upper()
		if str(self.titleId) != id:
			raise IndexError('Title IDs do not match!  ' + str(self.titleId) + ' != ' + id)

		decKey = Keys.decryptTitleKey(uhx(self.titleKey), ncaHeader.masterKey)

		pfs0 = Fs.PFS0(self.sectionHeaderBlock)

		'''
		print('encKey = ' + str(self.titleKey))
		print('decKey = ' + str(hx(decKey)))
		print('master key = ' + str(ncaHeader.masterKey))
		print('ctr = ' + str(hx(pfs0.cryptoCounter)))
		print('offset = ' + str(self.pfs0Offset))
		'''

		mem = File.MemoryFile(self.pfs0Header, Type.Crypto.CTR, decKey, pfs0.cryptoCounter, offset = self.pfs0Offset)
		magic = mem.read()[0:4]
		if magic != b'PFS0':
			raise LookupError('Title Key is incorrect!')

		return True

	def serialize(self):
		obj = {}
		obj['titleId'] = self.titleId
		obj['titleKey'] = self.titleKey

		obj['ncaHeader'] = hx(self.ncaHeader).decode()
		obj['sectionHeaderBlock'] = hx(self.sectionHeaderBlock).decode()
		obj['pfs0Header'] = hx(self.pfs0Header).decode()
		obj['pfs0Offset'] = self.pfs0Offset
		return obj

	def deserialize(self, obj):
		self.titleId = obj['titleId']
		self.titleKey = obj['titleKey']

		self.ncaHeader = uhx(obj['ncaHeader'])
		self.sectionHeaderBlock = uhx(obj['sectionHeaderBlock'])
		self.pfs0Header = uhx(obj['pfs0Header'])
		self.pfs0Offset = obj['pfs0Offset']
		return self

class Block:
	def __init__(self, index = None, timestamp = None, transactions = None, previous_hash = None, json = None):
		self.index = index
		self.timestamp = timestamp
		self.transactions = transactions
		self.previous_hash = previous_hash

		if json:
			self.deserialize(json)

	def hash(self):
		block_string = json.dumps(self.serialize(), sort_keys=True).encode()
		return hashlib.sha256(block_string).hexdigest()

	def serialize(self):
		obj = {}
		obj['index'] = self.index
		obj['timestamp'] = self.timestamp
		obj['transactions'] = []
		for t in self.transactions:
			obj['transactions'].append(t.serialize())
		obj['previous_hash'] = self.previous_hash
		return obj

	def deserialize(self, obj):
		self.index = obj['index']
		self.timestamp = obj['timestamp']
		self.transactions = []
		for t in obj['transactions']:
			self.transactions.append(KeyEntry(json = t))
		self.previous_hash = obj['previous_hash']
		return self

class Blockchain:
	def __init__(self):
		self.current_transactions = []
		self.chain = []
		self.nodes = set()

		self.load()

		if len(self.chain) == 0:
			# Create the genesis block
			self.new_block(previous_hash='1')

	def save(self):
		with open('titledb/blockchain.json', 'w') as outfile:
			obj = []
			for i in self.chain:
				obj.append(i.serialize())
			json.dump(obj, outfile, indent=4)

	def load(self):
		try:
			if os.path.isfile('titledb/blockchain.json'):
				with open('titledb/blockchain.json', encoding="utf-8-sig") as f:
					self.chain = []

					for j in json.loads(f.read()):
						self.chain.append(Block(json=j))
		except:
			pass

	def hasTitle(self, id):
		for c in self.chain:
			for t in c.transactions:
				if t.titleId == id:
					return True
		return False

	def register_node(self, address):
		"""
		Add a new node to the list of nodes

		:param address: Address of node. Eg. 'http://192.168.0.5:5000'
		"""

		parsed_url = urlparse(address)
		if parsed_url.netloc:
			self.nodes.add(parsed_url.netloc)
		elif parsed_url.path:
			# Accepts an URL without scheme like '192.168.0.5:5000'.
			self.nodes.add(parsed_url.path)
		else:
			raise ValueError('Invalid URL')


	def valid_chain(self, chain):
		"""
		Determine if a given blockchain is valid

		:param chain: A blockchain
		:return: True if valid, False if not
		"""

		last_block = chain[0]
		current_index = 1

		while current_index < len(chain):
			block = chain[current_index]
			print(f'{last_block}')
			print(f'{block}')
			print("\n-----------\n")
			# Check that the hash of the block is correct
			last_block_hash = self.hash(last_block)
			if block['previous_hash'] != last_block_hash:
				return False

			# Check that the title key is correct
			#if not self.valid_proof(last_block['proof'], block['proof'], last_block_hash):
			#	return False

			last_block = block
			current_index += 1

		return True

	def resolve_conflicts(self):
		"""
		This is our consensus algorithm, it resolves conflicts
		by replacing our chain with the longest one in the network.

		:return: True if our chain was replaced, False if not
		"""

		neighbours = self.nodes
		new_chain = None

		max_length = len(self.chain)

		for node in neighbours:
			response = requests.get(f'http://{node}/chain')

			if response.status_code == 200:
				length = response.json()['length']
				chain = response.json()['chain']

				if length > max_length and self.valid_chain(chain):
					max_length = length
					new_chain = chain

		if new_chain:
			self.chain = new_chain
			return True

		return False

	def new_block(self, previous_hash = None):
		if not previous_hash:
			previous_hash = blockchain.last_block.hash()

		block = Block(len(self.chain) + 1, time(), self.current_transactions, previous_hash or self.hash(self.chain[-1]))

		self.current_transactions = []

		self.chain.append(block)

		self.save()

		return block

	# ncaHeader = 0x4000 bytes, pfs0Header = 0x2000 bytes, titleKey = 0x10 bytes
	def new_transaction(self, keyEntry):
		if self.hasTitle(keyEntry.titleId):
			raise LookupError('Title ID already exists')

		if not keyEntry.verify():
			raise LookupError('Verification failed: bad key')

		self.current_transactions.append(keyEntry)

		return self.last_block.index + 1

	def suggest(self, titleId, titleKey):
		if not titleId or not titleKey:
			raise IndexError('Missing values')

		titleId = titleId.upper()
		nsp = Nsps.getByTitleId(titleId)

		if not nsp:
			raise IOError('Title not found: ' + titleId)

		nsp.open()

		for f in nsp:
			if type(f) == Fs.Nca and f.header.contentType == Type.Content.PROGRAM:
				for fs in f.sectionFilesystems:
					if fs.fsType == Type.Fs.PFS0 and fs.cryptoType == Type.Crypto.CTR:
						f.seek(0)
						ncaHeader = f.read(0x400)

						sectionHeaderBlock = fs.buffer

						f.seek(fs.offset)
						pfs0Header = f.read(0x10)

						entry = KeyEntry(titleId, titleKey.upper(), ncaHeader, sectionHeaderBlock, pfs0Header, fs.offset)

						index = blockchain.new_transaction(entry)

						blockchain.new_block()

						return True

			if type(f) == Fs.Nca and f.header.contentType == Type.Content.UNKNOWN:
				for fs in f.sectionFilesystems:
					if fs.fsType == Type.Fs.ROMFS and fs.cryptoType == Type.Crypto.CTR:
						f.seek(0)
						ncaHeader = f.read(0x400)

						sectionHeaderBlock = fs.buffer

						f.seek(self.ivfc.levels[0].offset)
						pfs0Header = f.read(self.ivfc.levels[0].size)

						entry = KeyEntry(titleId, titleKey.upper(), ncaHeader, sectionHeaderBlock, pfs0Header, self.ivfc.levels[0].offset)

						index = blockchain.new_transaction(entry)

						blockchain.new_block()

		return False

	@property
	def last_block(self):
		return self.chain[-1]


# Instantiate the Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
	try:
		values = request.get_json()

		# Check that the required fields are in the POST'ed data
		required = ['titleId', 'titleKey', 'ncaHeader', 'sectionHeaderBlock', 'pfs0Header', 'pfs0Offset']
		if not all(k in values for k in required):
			return 'Missing values', 400

		entry = KeyEntry(values['titleId'], values['titleKey'], values['ncaHeader'], values['sectionHeaderBlock'], values['pfs0Header'], values['pfs0Offset'])


		# Create a new Transaction
		index = blockchain.new_transaction(entry)

		blockchain.new_block()

		response = {'message': f'Transaction will be added to Block {index}'}
		return jsonify(response), 201
	except BaseException as e:
		return str(e), 400

@app.route('/transactions/suggest', methods=['GET'])
def new_suggestion():
	try:
		titleId = request.args.get('titleId')
		titleKey = request.args.get('titleKey')

		# Check that the required fields are in the POST'ed data
		required = ['titleId', 'titleKey']
		if not titleId or not titleKey:
			return 'Missing values', 400

		titleId = titleId.upper()
		nsp = Nsps.getByTitleId(titleId)

		if not nsp:
			return 'Title not found', 400

		nsp.open()

		for f in nsp:
			if type(f) == Fs.Nca and f.header.contentType == Type.Content.PROGRAM:
				for fs in f.sectionFilesystems:
					if fs.fsType == Type.Fs.PFS0 and fs.cryptoType == Type.Crypto.CTR:
						f.seek(0)
						ncaHeader = f.read(0x400)

						sectionHeaderBlock = fs.buffer

						f.seek(fs.offset)
						pfs0Header = f.read(0x10)

						entry = KeyEntry(titleId, titleKey.upper(), ncaHeader, sectionHeaderBlock, pfs0Header, fs.offset)

						index = blockchain.new_transaction(entry)

						blockchain.new_block()

						response = {'message': f'Transaction will be added to Block {index}'}
						return jsonify(response), 201

		return 'Verification failed: unable to locate correct title rights partition', 400
	except BaseException as e:
		return str(e), 400


@app.route('/chain', methods=['GET'])
def full_chain():
	response = {
		'chain': blockchain.chain,
		'length': len(blockchain.chain),
	}
	return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
	values = request.get_json()

	nodes = values.get('nodes')
	if nodes is None:
		return "Error: Please supply a valid list of nodes", 400

	for node in nodes:
		blockchain.register_node(node)

	response = {
		'message': 'New nodes have been added',
		'total_nodes': list(blockchain.nodes),
	}
	return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
	replaced = blockchain.resolve_conflicts()

	if replaced:
		response = {
			'message': 'Our chain was replaced',
			'new_chain': blockchain.chain
		}
	else:
		response = {
			'message': 'Our chain is authoritative',
			'chain': blockchain.chain
		}

	return jsonify(response), 200


def run(host='0.0.0.0', port=5000):
	app.run(host, port)
