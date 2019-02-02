import hashlib
import json
import uuid


class Transaction(object):
    """
    Represents a bitcoin transaction.

    These transactions are inturn added to the merkle tree for quick retrieval.
    """

    def __init__(self, *args):
        """
        An instance of the transaction.

        :param args: Contains source, destination and payload.
        """
        if any([arg is None for arg in args]):
            raise ValueError('Arguments passed to Transaction are incorrect. %s' % (' '.join([str(arg)
                                                                                              for arg in args]
                                                                                             )))
        self._id, self.source, self.dest, self.payload = args

    def __eq__(self, other):
        return (self.source == other.source and
                self.dest == other.dest and
                self._id == other._id and
                self.payload == other.payload)

    def __str__(self):
        return '%s' % self._id

    def to_dict(self):
        return {'_id'    : self._id,
                'source' : self.source,
                'dest'   : self.dest,
                'payload': self.payload}

    def __hash__(self):
        return hash(str(self))

    def encode(self):
        return hashlib.sha256(str(self).encode('utf-8')).hexdigest()

    def to_json(self):
        return json.dumps(self.to_dict())


class CoinBaseTransaction(Transaction):
    def __init__(self, dest_addr):
        """
        Create the Coinbase transaction.

        It contains the source as C{COINBASE} and the destination as the miner's address.
        """
        _id = str(uuid.uuid4())
        source = "COINBASE"
        dest = dest_addr
        payload = 10  # TODO: sum inputs -sum outputs
        super().__init__(_id, source, dest, payload)

    def __hash__(self):
        return hash((self._id, self.source, self.dest, self.payload))


def validate_transaction(transaction):
    """TODO: This is not yet done completely."""
    return True
