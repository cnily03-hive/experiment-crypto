import random
from Crypto.Util.number import bytes_to_long, long_to_bytes
from sympy import mod_inverse


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

def rsa_encrypt(m, e, n):
    return pow(m, e, n)

def rsa_decrypt(c, d, n):
    return pow(c, d, n)

def get_coprime(phi):
    while True:
        e = random.randint(2, phi)
        if miller_rabin(e) and mod_inverse(e, phi):
            return e

p = prime_nbit(1024)
q = prime_nbit(1024)

print(f'p = {p}')
print(f'q = {q}')

phi = (p - 1) * (q - 1)

e = get_coprime(phi)
n = p * q
d = mod_inverse(e, phi)

print(f'e = {e}')
print(f'd = {d}')

m = bytes_to_long(b'Hello, RSA!')
print(f'm = {m}')

cipher = rsa_encrypt(m, e, n)
print(f'cipher = {cipher}')

dec = rsa_decrypt(cipher, d, n)

print(long_to_bytes(dec))