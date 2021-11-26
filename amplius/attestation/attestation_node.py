import os
import subprocess
import sys
import binascii
import requests
import json
from web3 import Web3

from . import attestation_contract
from . import merkle_tree_hashing
from . import data_coding

# for proof-of-authority geth nodes, development
#from web3.middleware import geth_poa_middleware

class AttestationNode:

	def __init__(self, working_dir):
		self.working_dir = working_dir

	def run_node(self):
		os.makedirs(self.working_dir, exist_ok=True)
		os.chdir(self.working_dir)

class GethNode(AttestationNode):

	GETH = "geth"
	
	GETH_DATADIR = "geth-data"
	GETH_DATADIR_POA = "geth-data-poa"
	
	GETH_DATADIR_ANCIENT = "geth-data-ancient"
	GETH_DATADIR_ANCIENT_POA = "geth-data-ancient-poa"

	GETH_DAG_DIR = "geth-dag"

	def __init__(self, working_dir):
		super().__init__(working_dir)

	def run_node(self, account_address, account_password_file):
		super().run_node()
		subprocess.run([self.GETH, "--datadir", self.GETH_DATADIR, "datadir.ancient", self.GETH_DATADIR_ANCIENT, "--ethash.dagdir", self.GETH_DAG_DIR, "--cache", 4000, "--syncmode", "full", "--ws", "--ws.api", "eth,net,web3"])
	
	def run_node_poa_development(self, account_address, account_password_file):
		super().run_node()
		subprocess.run([self.GETH, "--datadir", self.GETH_DATADIR_POA, "datadir.ancient", self.GETH_DATADIR_ANCIENT_POA, "--cache", 4000, "--syncmode", "full", "--rpccorsdomain", "*", "networkid", 55194, "--nodiscover", "--vmdebug"])
		# --unlock "0xf7b13d6b33EC6492AfB9756205D1A9e58Bab70ee" -allow-insecure-unlock console

class Web3Attestation(AttestationNode):

	# Node Web Socket Connection
	#WEB3_ADDRESS = "ws://x:46804"
	WEB3_ADDRESS = "wss://mainnet.infura.io/ws/v3/5cc53e4f3f614825be68d6aae4897cf4"

	# Node HTTP Connection
	#WEB3_ADDRESS = "http://127.0.0.1:8545"
	#WEB3_ADDRESS = "https://mainnet.infura.io/v3/5cc53e4f3f614825be68d6aae4897cf4"

	def __init__(self, identity):
		self.ci_account_address = Web3.toChecksumAddress(identity.address)
		self.ci_account_privatekey = identity.privatekey

		if self.WEB3_ADDRESS.startswith("ws"):
			provider = Web3.WebsocketProvider(self.WEB3_ADDRESS, websocket_timeout=3)
		else:
			provider = Web3.HTTPProvider(self.WEB3_ADDRESS)
		
		self.w3 = Web3(provider)

		# for proof-of-authority:
		#self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
		
		self.att_contract = None

	def get_attestation_contract(self):
		if self.att_contract is None:
			self.att_contract = self.w3.eth.contract(address=attestation_contract.ADDRESS, abi=attestation_contract.ABI)
		return self.att_contract

	def get_current_gas_price(self):
		gas_price_api = "https://www.etherchain.org/api/gasPriceOracle"
		r = requests.get(gas_price_api).json()
		gas_price = Web3.toWei(r['fastest'], 'gwei')

		if gas_price > 100000000000:
			print("Gas price exceeds 100 Gwei, abort")
			sys.exit()

		return gas_price

	def get_transaction(self):
		nonce = self.w3.eth.getTransactionCount(self.ci_account_address)
		#block = self.w3.eth.getBlock("latest")

		gas_price = self.get_current_gas_price()
		gas_limit = 300000

		tx = {
				"from": self.ci_account_address,
				"value": 0,
				'chainId': 1,
				'nonce': nonce,
				'gas': gas_limit,
				'gasPrice': gas_price
		}

		print("Gas limit:", gas_limit)
		print("Gas price:", gas_price)

		return tx

	def send_transaction(self, tx):
		tx_hash = ""
		pk_b = self.ci_account_privatekey
		signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=pk_b)
		print(signed_tx)
		#signed_tx.r / s / v
		tx_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
		return tx_hash

	def register_uri_scheme_authority(self, scheme, authority):

		print("Retrieve or register URI scheme", scheme, "and URI authority", authority, "...\n")

		scheme_bytes32 = data_coding.encode_str_bytes32(scheme)
		authority_bytes32 = data_coding.encode_str_bytes32(authority)

		att_contract = self.get_attestation_contract()
		s_id = att_contract.functions.retrieveUriSchemeIndex(scheme_bytes32).call()
		a_id = att_contract.functions.retrieveUriAuthorityIndex(authority_bytes32).call()

		if s_id == 0 and len(scheme) >= 0:
			transaction = self.get_transaction()
			print("Registering URI scheme", scheme, "...")
			tx = att_contract.functions.registerUriScheme(scheme_bytes32).buildTransaction(transaction)
			tx_hash = self.send_transaction(tx)
			receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)
			s_id = att_contract.caller.retrieveUriSchemeIndex(scheme_bytes32)
			print(receipt)

		if a_id == 0 and len(authority) >= 0:
			transaction = self.get_transaction()
			print("Registering URI authority", authority, "...")
			tx = att_contract.functions.registerUriAuthority(authority_bytes32).buildTransaction(transaction)
			tx_hash = self.send_transaction(tx)
			receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)
			a_id = att_contract.caller.retrieveUriAuthorityIndex(authority_bytes32)
			print(receipt)

		print("URI scheme ID", s_id)
		print("URI authority ID", a_id, end="\n\n")
		return (s_id, a_id)

	def register_mime_type(self, mime_type):
		print("Retrieve or register MIME type ... \n")
		att_contract = self.get_attestation_contract()
		mime_type_bytes32 = data_coding.encode_str_bytes32(mime_type)
		m_id = att_contract.caller.retrieveMimeTypeIndex(mime_type_bytes32)

		if m_id == 0 and len(mime_type) > 0:
			transaction = self.get_transaction()
			print("Registering MIME type", mime_type, "...")
			tx = att_contract.functions.registerMimeType(mime_type_bytes32).buildTransaction(transaction)
			tx_hash = self.send_transaction(tx)
			receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)
			m_id = att_contract.caller.retrieveMimeTypeIndex(mime_type_bytes32)

		if m_id > 0:
			print("Retrieved MIME type ID", m_id, "for", mime_type)
		print()

		return m_id

	def issue_claim(self, merkle_root, uri_scheme_IDs, uri_authority_IDs, uri_paths, file_set_ext_marker, mime_type_id):
		if self.w3.isConnected():
			att_contract = self.get_attestation_contract()

			merkle_root_bytes32 = data_coding.encode_binary_bytes32(merkle_root)
			uri_paths_bytes32 = data_coding.encode_str_list_bytes32(uri_paths)

			# recordClaim(bytes32 merkleRoot, uint16 schemeID, uint16 authorityID, uint16 mimeTypeID,
			# bytes32 path, bool hasURIExtension, bytes32 externalDID)
			print("\nRecording claim for URI schemes", uri_scheme_IDs, "with URI authorities", uri_authority_IDs, "...\n")
			transaction = self.get_transaction()
			tx = att_contract.functions.recordClaim(
				merkle_root_bytes32, uri_scheme_IDs, uri_authority_IDs, uri_paths_bytes32, file_set_ext_marker, mime_type_id).buildTransaction(transaction)
			tx_hash = self.send_transaction(tx)
			receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)
			record_id = att_contract.functions.getNClaimRecords(merkle_root_bytes32).call()

			# recordClaimURIExtension(bytes32 merkleRoot, uint8 claimRecordID, uint8 extensionID, bytes16 extension,
			# bool isAlternativePath, bool hasNext)
			
			print("Claim recorded with Merkle root: 0x", bytes.hex(merkle_root), ", record ID: ", record_id, sep="", end="\n\n")
		else:
			print("Error: web3 is not connected to blockchain node", self.WEB3_ADDRESS)

	def link(self, link_id, merkle_root, parent_link_id):
		if self.w3.isConnected():
			att_contract = self.get_attestation_contract()

			link_id_bytes32 = data_coding.encode_str_bytes32(link_id)
			link_id_bytes32 = data_coding.encode_str_bytes32(link_id)
			merkle_root_bytes32 = data_coding.encode_binary_bytes32(merkle_root)
			parent_link_id_bytes32 = data_coding.encode_str_bytes32(parent_link_id)
			#print("Merkle Root byte format:", binascii.hexlify(merkle_root_bytes32))
			#print("Link ID byte format:", binascii.hexlify(link_id_bytes32))

			print("Creating link", link_id, "to", merkle_root, "...")
			transaction = self.get_transaction()
			tx = att_contract.functions.link(link_id_bytes32, merkle_root_bytes32, parent_link_id_bytes32).buildTransaction(transaction)
			tx_hash = self.send_transaction(tx)
			receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)

	def resolve_link(self, link_id):
		if self.w3.isConnected():
			att_contract = self.get_attestation_contract()
			link_id_bytes32 = data_coding.encode_str_bytes32(link_id)
			print("Link ID byte format:", binascii.hexlify(link_id_bytes32))

			(mr_bytes32, link_issuer, par_id_bytes32, n_records) = att_contract.functions.resolveLink(link_id_bytes32).call()
			merkle_root = data_coding.decode_binary_bytes32(mr_bytes32)
			parent_link_id = data_coding.decode_str_bytes32(par_id_bytes32)

			print("Resolved link", link_id, "to claim", merkle_root)

			return (merkle_root, link_issuer, parent_link_id, n_records)

	def get_storage_metadata(self, merkle_root, record_id):
		if self.w3.isConnected():
			att_contract = self.get_attestation_contract()
			merkle_root_bytes32 = data_coding.encode_binary_bytes32(merkle_root)

			#print("Merkle root byte format:", merkle_root_bytes32)
			#print("Record ID:", record_id)
			(mime_b, ts) = att_contract.functions.getStorageMetadata(merkle_root_bytes32, record_id).call()

			mime = data_coding.decode_str_bytes32(mime_b)

			#print("Retrieved storage metadata for Merkle root", merkle_root)

			return (mime, ts)

	def get_storage_metadata_uris(self, merkle_root, record_id, uri_id):
		if self.w3.isConnected():
			att_contract = self.get_attestation_contract()
			merkle_root_bytes32 = data_coding.encode_binary_bytes32(merkle_root)

			#print("Merkle root byte format:", merkle_root_bytes32)
			#print("Record ID:", record_id)
			#print("URI ID:", uri_id)
			(file_set_ext_marker, sh_id, auth_id, path_b) = att_contract.functions.getStorageMetadataURIs(merkle_root_bytes32, record_id, uri_id).call()

			#print("Retrieved storage metadata for Merkle root", merkle_root)

			return (file_set_ext_marker, sh_id, auth_id, path_b)

	def get_uri_schema(self, s_id):
		if self.w3.isConnected():
			att_contract = self.get_attestation_contract()
			sh_b = att_contract.functions.uriSchemeRegistry(s_id).call()
			sh = data_coding.decode_str_bytes32(sh_b)
			return sh

	def get_uri_authority(self, a_id):
		if self.w3.isConnected():
			att_contract = self.get_attestation_contract()
			auth_b = att_contract.functions.uriAuthorityRegistry(a_id).call()
			auth = data_coding.decode_str_bytes32(auth_b)
			return auth

	def get_issuer_metadata(self, merkle_root, record_id):
		if self.w3.isConnected():
			att_contract = self.get_attestation_contract()
			merkle_root_bytes32 = data_coding.encode_binary_bytes32(merkle_root)

			#print("Merkle root byte format:", merkle_root_bytes32)
			#print("Record ID:", record_id)
			(addr, ext_id_b) = att_contract.functions.getIssuerMetadata(merkle_root_bytes32, record_id).call()
			ext_id = data_coding.decode_str_bytes32(ext_id_b)

			#print("Retrieved issuer metadata for Merkle root", merkle_root)

			return (addr, ext_id)
	def get_n_claim_records(self, merkle_root):
		if self.w3.isConnected():
			att_contract = self.get_attestation_contract()

			merkle_root_bytes32 = data_coding.encode_binary_bytes32(merkle_root)
			n_claim_records = att_contract.functions.getNClaimRecords(merkle_root_bytes32).call()

			return n_claim_records

	def validate_claim(self, merkle_root, record_id):
		if self.w3.isConnected():
			att_contract = self.get_attestation_contract()

			merkle_root_bytes32 = data_coding.encode_binary_bytes32(merkle_root)
			merkle_root_prime_bytes32 = data_coding.encode_binary_bytes32(merkle_root)

			(is_valid, ci_account_address, timestamp) = att_contract.functions.validateClaim(merkle_root_bytes32, record_id, merkle_root_prime_bytes32).call()
			
			return (is_valid, ci_account_address, timestamp)
