import hashlib

from constants import HASH_FUNCTION


def is_power_of_two(n):
    """Check whether `n` is an exponent of two
    """
    return n != 0 and ((n & (n - 1)) == 0)


def hash_data(data):
    """One-way function, takes various standard algorithm names as
    `hash_function` input and uses it to hash string `data`. The default
    algorithm is 'sha256'. Even small changes in `data` input cause
    significant changes to the output"""

    hash_function = getattr(hashlib, HASH_FUNCTION)
    data = data.encode('utf-8')
    return hash_function(data).hexdigest()


def concat_and_hash_list(lst, hash_function='sha256'):
    """Helper function for quickly concatenate pairs of values and hash them.
        The process is repeated until one value is returned: the final hash.
        Assumes that the length of the `lst` is an exponent of two"""

    assert len(lst) >= 2, "No transactions to be hashed"
    while len(lst) > 1:
        a = lst.pop(0)
        b = lst.pop(0)
        lst.append(hash_data(a + b))
    return lst[0]
