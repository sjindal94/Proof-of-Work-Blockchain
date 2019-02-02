"""
Block Module Implementation
"""
import hashlib
import json
from collections import OrderedDict

from constants import DIFFICULTY
from merkletree import MerkleTree
from transaction import Transaction

SYS_VERSION = "0.1"
HEADER_FIELDS = ["Version", "Previous_Block_Hash", "Merkle_Root", "Timestamp", "Difficulty_Target", "Nonce"]


class BlockHeader(object):
    """Block Header class (property of a block)"""

    @property
    def headlist(self):
        return (self.version, self.previous_hash, self.merkle_root.block_header,
                self.timestamp, self.difficulty_bits, self.nonce)


BLOCK_INSTANCE_VARS = ['size', 'version', 'index', 'tx_list', 'previous_hash',
                       'timestamp', 'difficulty_bits', 'nonce', 'tx_cnt']


class Block(BlockHeader):
    """A class representing the block module in the blockchain"""

    def __init__(self, *args, nonce=0):
        """
        :param index: Index of the block
        :param previous_hash: Hash of previous block
        :param timestamp: Timestamp property
        :param difficulty_bits: Difficulty Bits set for the blockchain
        :param nonce: Nonce calculated using Proof Of Work Consensus
        """
        if any([arg is None for arg in args]):
            raise ValueError('Arguments passed to Block are incorrect. %s' % (' '.join([str(arg)
                                                                                        for arg in args])))

        self.version = SYS_VERSION

        (self.index, self.tx_list, self.previous_hash,
         self.timestamp, self.difficulty_bits) = args

        self.nonce = nonce

    @property
    def size(self):
        # FIXME: Not sure about utility
        return 9

    @property
    def tx_cnt(self):
        return len(self.tx_list)

    @property
    def merkle_root(self):
        return MerkleTree(self.tx_list)

    def __str__(self):
        jsondict = {col: self.__dict__[col]
                    for col in self.__dict__
                    if col in BLOCK_INSTANCE_VARS}

        jsondict.pop('tx_list')

        jsondict['blockhash'] = self.blockhash
        jsondict['merkleroot'] = self.merkle_root.block_header

        return "%s\n" % json.dumps(jsondict, indent=4)

    def to_json(self):
        """Convert the block to a JSON format for transmitting across the network."""
        jsondict = {col: self.__dict__[col]
                    for col in self.__dict__
                    if col in BLOCK_INSTANCE_VARS}

        json_list = []

        for x in jsondict['tx_list']:
            json_list.append(x.to_json())

        jsondict['tx_list'] = json_list
        jsondict['blockhash'] = self.blockhash

        return json.dumps(jsondict)

    @property
    def blockhash(self):
        """
        The hash of the given block.

        :param self: Block properties
        :return: Hash of the block header
        """
        header = ' '.join([str(col)
                           for col in self.headlist])
        header = header.encode('utf-8')
        return hashlib.sha256(header).hexdigest()

    def __eq__(self, other_block):
        """
        :param other_block: Other Block instance
        :return: Check if the other_block is equal to the given block or not
        """
        if isinstance(other_block, Block):
            return self.blockhash == other_block.blockhash

        return False


class GenesisBlock(Block):
    """A class representing the genesis block for the blockchain"""

    def __init__(self):
        block_data = OrderedDict([('index', 0),
                                  ('tx_list', [Transaction("0ef7416c-da9a-4944-a47a-b7fec8cd4db1", "src", "dest", 0)]),
                                  ('previous_hash', "0"),
                                  ('timestamp', 141385154705),
                                  ('difficulty_bits', DIFFICULTY)])

        nonce = 1
        super().__init__(*block_data.values(), nonce=nonce)


BLOCK_CONSTRUCTION_PARAMS = ('index', 'tx_list', 'previous_hash', 'timestamp', 'difficulty_bits', 'nonce')


def validate_block_struct(obj_dict, blockchain_obj):
    for col in BLOCK_CONSTRUCTION_PARAMS:
        if col not in obj_dict.keys():
            return False

    if blockchain_obj.parent_exist(obj_dict['previous_hash']):
        if (blockchain_obj.block_index(obj_dict['previous_hash']) + 1) != obj_dict['index']:
            return False
    else:
        return False

    if obj_dict['tx_list'][0].source != "COINBASE":
        return False

    try:
        transactions = []
        for tx in obj_dict['tx_list']:
            tx = json.loads(tx.to_json())
            transactions.append(Transaction(tx['_id'], tx['source'], tx['dest'], tx['payload']))

        obj_dict['tx_list'] = transactions

        testBlock = Block(obj_dict['index'], obj_dict['tx_list'], obj_dict['previous_hash'],
                          obj_dict['timestamp'], obj_dict['difficulty_bits'],
                          nonce=obj_dict['nonce'])

        test_hash = testBlock.blockhash
        test_target = 2 ** (256 - DIFFICULTY)

        if int(test_hash, 16) >= test_target:
            print("Wrong in POW")
            return False

        return True
    except ValueError as e:
        print(e)
        return False
