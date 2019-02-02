from block import Block, GenesisBlock
from collections import defaultdict
from constants import DIFFICULTY
from datetime import datetime
from transaction import CoinBaseTransaction

import json


class Blockchain(object):
    """A class representing list of blocks"""

    def __init__(self):
        """
        A representation of the blockchain.

        @ivar _chaingraph: A graph representation of the blocks, where a block and its children are linked.
        @ivar blockmap: A mapping of the block hash to the Block structure
        @ivar difficulty_bits: Current difficulty set for the Proof of Work
        """
        self._chaingraph = defaultdict(set)
        self.blockmap = defaultdict()
        self.difficulty_bits = DIFFICULTY
        self.addGenesis()

    def __str__(self):
        return "Chain Length: %s\n" % self.max_height

    @property
    def chain(self):
        """Created a dict containing list of block objects to view."""
        return self.dict(self._chaingraph)

    def addGenesis(self):
        """
        Add genesis block the blockchain as the first block.

        - Create Genesis Block
        - Add it to the blockmap and set the chain graph.
        """
        self.primary_blockchain_block = GenesisBlock()
        self.blockmap[self.primary_blockchain_block.blockhash] = self.primary_blockchain_block
        self._chaingraph[self.primary_blockchain_block.blockhash] = set()
        self.max_height = 1

    def dict(self, chain):
        """Converts list of block objects to dictionary."""
        return json.loads(json.dumps(chain, default=lambda o: o.__dict__))

    def reset(self):
        """Resets the blockchain blocks except genesis block"""
        self._chaingraph = [self._chaingraph[0]]

    def get_latest_block(self):
        """Gets the last block from the blockchain from its primary chain."""
        try:
            return self.primary_blockchain_block
        except IndexError as _:
            return None

    def parent_exist(self, parent_hash):
        """Check whether the C{parent_hash} is present in the blockchain."""
        return parent_hash in self._chaingraph

    def block_index(self, block_hash):
        """Get the index of a given C{block_hash}."""
        return self.blockmap[block_hash].index

    def create_block(self, block_data):
        """
        Creates a new block with the given block data

        1. Get latest block in the chain.
        2. Compute new index and timestamp
        3. Return newly created candidate block without the proof of work.
        """
        # print("CREATE_BLOCK")
        latest_block = self.get_latest_block()
        previous_block_hash = latest_block.blockhash
        next_index = latest_block.index + 1
        next_timestamp = datetime.now().strftime("%s")
        candidate_block = Block(next_index, block_data, previous_block_hash, next_timestamp, self.difficulty_bits)

        return candidate_block

    def mine_block(self, pending_tx, miner_id):
        """
        Mine a new block with the pending transactions.

        This involves adding the coinbase transaction to the pending transaction.
        Use L{self.create_block} to create the new block.

        NOTE: Proof of work is not done yet.
        """
        pending_tx.insert(0, CoinBaseTransaction(miner_id))
        return self.create_block(pending_tx)

    def add_block(self, transactions=None, block=None):
        """
        Add a block to the blockchain.

        If transaction are passed then a new block is created before getting added.
        If block is passed it is directly added.
        """
        if transactions is not None:
            block = self.create_block(transactions)

        hash = block.blockhash
        if hash not in self._chaingraph:
            self._chaingraph[hash] = set()

        self._chaingraph[block.previous_hash].add(hash)
        self.blockmap[hash] = block

        if block.previous_hash == self.primary_blockchain_block.blockhash:
            self.primary_blockchain_block = block
            self.max_height += 1
        else:
            height1 = len(self.block_ancestory(self.blockmap[block.blockhash]))

            if height1 > self.max_height:
                self.primary_blockchain_block = block
                self.max_height = height1

    def block_ancestory(self, block):
        """Get all the ancestors of the given C{block} till the genesis block."""
        list_ = []
        while block.previous_hash is not "0":
            list_.append(block)
            block = self.blockmap[block.previous_hash]

        list_.append(block)  # genesis block

        return list_
