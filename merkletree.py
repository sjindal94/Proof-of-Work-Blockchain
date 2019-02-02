from utils import is_power_of_two, hash_data


class MerkleLeaf(object):
    """
    Attach two pieces of string data and store the hash of the concatenated strings
    """

    def __init__(self, left, right):
        self._left = left
        self._right = right
        self.height = 1

    @property
    def data(self):
        """str: Allow the user to query the hashed data stored in the
        MerkleLeaf
        """
        return hash_data(self._left.encode() + self._right.encode())


class MerkleNode(MerkleLeaf):
    """
    Attach two MerkleLeaf structures and store the hash of their concatenated data
    """

    def __init__(self, left, right):
        super().__init__(left, right)
        self.height = self._left.height + 1

    @property
    def data(self):
        """Ensure data is in the form of a HashLeaf data structures and has
        the correct height. Separate method from `HashLeaf` as there are
        different requirements
        """
        # assert isinstance(self._left, MerkleLeaf), "Data is not of type `MerkleLeaf`"
        # assert isinstance(self._right, MerkleLeaf), "Data is not of type `MerkleLeaf`"

        assert self._left.height == self._right.height, "Left and right branch not balanced"

        return hash_data(self._left.data + self._right.data)


class MerkleTree(object):
    """Implementation of MerkleTree for each Node"""

    def __init__(self, tx_list):
        self._leaves = list(tx_list)
        self._nodes = []
        self._root = self._build_merkle_tree()
        self._block_header = self._root.data

    def add_transaction(self, tx):
        """Add an arbitrary amount of tx's to the tree. It needs to be
        reconstructed every time this happens and the block header
        changes as well
        """
        self._leaves.append(tx)
        self._rebuild_tree()

    def reset_tree(self):
        """Clear the tree data"""
        self._nodes = []
        self._block_header = None

    def _build_merkle_tree(self):
        """Used to construct the tree and arrive at the block header"""
        leaves, leaf_cnt = self._leaves, len(self._leaves)

        if not is_power_of_two(leaf_cnt) or leaf_cnt < 2:
            # duplicate last transaction till completely balanced
            last_tx = leaves[-1]
            while not is_power_of_two(leaf_cnt) or leaf_cnt < 2:
                leaves.append(last_tx)
                leaf_cnt += 1

        for tx in range(0, len(leaves), 2):
            self._nodes.append(MerkleLeaf(leaves[tx], leaves[tx + 1]))

        merkle_leaves = list(self._nodes)

        while len(merkle_leaves) > 2:
            left, right = merkle_leaves.pop(0), merkle_leaves.pop(0)
            merkle_node = MerkleNode(left, right)
            merkle_leaves.append(merkle_node)

        if len(merkle_leaves) == 1:
            return merkle_leaves[0]

        return MerkleNode(merkle_leaves[0], merkle_leaves[1])

    def _rebuild_tree(self):
        """Resets the tree and makes a call to `_evaluate(...)` to reconstruct
        the tree given its persistent list of tx's
        """
        self.reset_tree()
        self._root = self._build_merkle_tree()
        self._block_header = self._root.data

    @property
    def height(self):
        """int: Allow the user to query the tree's height"""
        return self._root.height

    @property
    def leaves(self):
        """list: Allow the user to query the tree's list of tx's"""
        return self._leaves

    @property
    def block_header(self):
        return self._block_header
