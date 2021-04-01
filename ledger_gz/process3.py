#simplejson can convert decimal to json
import simplejson as json
import os
import gzip
import time
#for logging exceptions
import logging
from datetime import timedelta, date, datetime
from decimal import *
from binascii import a2b_hex, b2a_hex
from blockchain_parser.blockchain import Blockchain
from blockchain_parser.output import Output
from blockchain_parser.transaction import Transaction
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
#from slickrpc import Proxy

start_time = time.monotonic()
def default(obj):
	if isinstance(obj, (date, datetime)):
		return obj.isoformat()
def parser(block):
	"""parse each block in the block chain"""
	blk={}
	blk['hash'] = block.hash
	blk['size'] = block.size
	blkheight=block.height
	blk['height']=blkheight
	blkhead = block.header
	blk['version']=blkhead.version
	blk['merkleroot']=blkhead.merkle_root
	blk['time']=blkhead.timestamp
	blk['bits']=blkhead.bits
	blk['difficulty']=blkhead.difficulty
	blk['nTx']=block.n_transactions
	blk['previousblockhash']=blkhead.previous_block_hash
	blk['tx']=[]
	for blktx in block.transactions:
		txinfo = {}
		blktxid=blktx.txid
		txinfo['txid']=blktxid
		txinfo['hash']=blktx.hash
		txinfo['version']=blktx.version
		txinfo['locktime']=blktx.locktime
		txinfo['vin']=[]
		txinfo['vout']=[]
		for input in blktx.inputs:
			prevtxinfo = {}
			prevtxinfo['sequence']=input.sequence_number
			#the parser already transformed the txid into a searchable form
			prevtxidhash=input.transaction_hash
			if(prevtxidhash == "0"*64):
				prevtxinfo['coinbase']="%s"%True
			else:
				#refer to a previous transaction with previous transaction's ID 
				#and the index of one of the outputs in this previous transaction  
				prevtxinfo['txid']=input.transaction_hash
				prevtxinfo['vout']=input.transaction_index
				prevtxinfo['scriptSig']={}
				prevtxinfo['scriptSig']['asm']=input.script.value
				prevtxinfo['scriptSig']['hex']=b2a_hex(input.script.script).decode('utf-8')
				#url = "/rest/tx/%s.hex"%prevtxidhash
				prevtxhex = rpc_connection.getrawtransaction(prevtxidhash,0)
				#prevtxbyt=proxy.request('GET',url).data.strip()
				prevtx=Transaction(a2b_hex(prevtxhex))
				prevtxouts=prevtx.outputs
				prevtxout=prevtxouts[input.transaction_index]
				prevtxoutval=Decimal(prevtxout.value)*Decimal(0.00000001)
				prevtxinfo['txvoutinfo']={}
				prevtxinfo['txvoutinfo']['type']=prevtxout.type
				prevtxinfo['txvoutinfo']['value']='%.8f'%prevtxoutval
				prevtxaddrs=prevtxout.addresses
				prevtxinfo['txvoutinfo']['addresses']=[addr.address for addr in prevtxaddrs]
			txinfo['vin'].append(prevtxinfo)
		outputindex=0
		for output in blktx.outputs:
			outputinfo={}
			outputval=Decimal(output.value)*Decimal(0.00000001)
			outputinfo['value']='%.8f'%outputval
			outputinfo['n']=outputindex
			outputinfo['scriptPubKey']={}
			outputinfo['scriptPubKey']['asm']=output.script.value
			outputinfo['scriptPubKey']['hex']=b2a_hex(output.script.script).decode('utf-8')
			#script may be invalid
			try:
				outputinfo['scriptPubKey']['type']=output.type
				outputaddrs=output.addresses
				outputinfo['scriptPubKey']['addresses']=[outputaddr.address for outputaddr in outputaddrs]
			except Exception as e:
				outputinfo['scriptPubKey']['type']="not available"
				outputinfo['scriptPubKey']['addresses']="not available"
				errormes="at block height=%d; txid=%s; output=%d; encounter %s"%(blkheight,blktxid,outputindex,e)
				print(errormes)
				logger.error(errormes)
				pass
			txinfo['vout'].append(outputinfo)
			outputindex += 1
		blk['tx'].append(txinfo)

	#Serializing to json and store as gz
	#writing to file named with block height
	#blkheight = blk.get("height")
	#if blkcount % 1000 == 0 :
	print("process3 %d"%blkheight)
	#filename=os.path.join(directory,"%s"%block.hash+".gz")
	filename=os.path.join(storagedir,"%d"%blkheight+".gz")
	#serializing into pickle
	with gzip.open(filename,"wt", encoding = "ascii") as outfile:
		json.dump(blk,outfile,indent=4,default=default)

# Create and configure logger
logging.basicConfig(filename="parser.log",format='%(asctime)s %(message)s', filemode='w')
# Create an object
logger = logging.getLogger()
# Setting the threshold of logger to DEBUT
logger.setLevel(logging.ERROR) 
# rpc_user and rpc_password are set in the bitcoin.conf file, please replace with your own
rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:8332"%('mango', 'fruitcoin20'))
# Instantiate the Blockchain by giving the path to the directory 
# containing the .blk files created by bitcoind
# default should be ~/.bitcoin/blocks, then it'll parse all the blocks up until today
directory = os.path.expanduser('~/.bitcoin/blocks')
blockchain = Blockchain(directory)
indexdir=os.path.expanduser('./index3')
storagedir=os.path.expanduser('./storagedir')
blocks=blockchain.get_ordered_blocks(indexdir, start=600915)
blkcount = 0
for block in blocks:
	parser(block)
	blkcount += 1


#time the process
end_time = time.monotonic()
#print(timedelta(seconds=end_time-start_time))
