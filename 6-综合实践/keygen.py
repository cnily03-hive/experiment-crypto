import random
from Crypto.Util.number import bytes_to_long, long_to_bytes
from sympy import mod_inverse
import math
from base64 import b64encode

def miller_rabin(n, k=5):
    if n == 2 or n == 3:
        return True
    if n < 2 or n % 2 == 0:
        return False

    # Write n - 1 as d * 2^s
    s, d = 0, n - 1
    while d % 2 == 0:
        s += 1
        d //= 2

    # Witness loop
    for _ in range(k):
        a = random.randint(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def prime_nbit(n):
    while True:
        p = random.getrandbits(n)
        # odd number, 2**(n-1) < p < 2**n
        p |= (1 << n - 1) | 1
        if miller_rabin(p):
            return p

def get_coprime(phi):
    while True:
        e = random.randint(2, phi)
        if miller_rabin(e) and mod_inverse(e, phi):
            return e

def gen_key():
    p = prime_nbit(1024)
    q = prime_nbit(1024)
    phi = (p - 1) * (q - 1)
    e = get_coprime(phi)
    n = p * q
    d = mod_inverse(e, phi)
    # public key: (e, n)
    # private key: (d, n)
    return (e, n), (d, n)

def long_to_base64(n):
    return b64encode(long_to_bytes(n)).decode()

if __name__ == '__main__':
    pubkey_t, privkey_t = gen_key()
    pubkey = (pubkey_t[0] << 2048) | pubkey_t[1]
    privkey = (privkey_t[0] << 2048) | privkey_t[1]
    print(f'e = {pubkey_t[0]}')
    print(f'd = {privkey_t[0]}')
    print(f'n = {pubkey_t[1]}')
    print(f'pubkey = \'{long_to_base64(pubkey)}\'')
    print(f'privkey = \'{long_to_base64(privkey)}\'')