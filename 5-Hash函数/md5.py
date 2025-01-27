import math
import struct

# Initialize variables
A = 0x67452301
B = 0xefcdab89
C = 0x98badcfe
D = 0x10325476

INIT_H = (A, B, C, D)

# Constants for MD5 transformation
S = [7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22,
     5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20,
     4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23,
     6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21]

K = [int(abs(math.sin(i + 1)) * 2**32) & 0xffffffff for i in range(64)]


# Functions for MD5 transformation


def left_rotate(x, amount):
    x &= 0xFFFFFFFF
    return ((x << amount) | (x >> (32 - amount))) & 0xFFFFFFFF


def md5_compress(chunk, h_list):
    a, b, c, d = h_list

    # 主循环，64步运算
    for i in range(64):
        if 0 <= i <= 15:
            F = (b & c) | (~b & d)
            g = i
        elif 16 <= i <= 31:
            F = (d & b) | (~d & c)
            g = (5 * i + 1) % 16
        elif 32 <= i <= 47:
            F = b ^ c ^ d
            g = (3 * i + 5) % 16
        elif 48 <= i <= 63:
            F = c ^ (b | ~d)
            g = (7 * i) % 16

        F = (F + a + K[i] + chunk[g]) & 0xffffffff
        a = d
        d = c
        c = b
        b = (b + left_rotate(F, S[i])) & 0xffffffff

    return [(x + y) & 0xffffffff for x, y in zip(h_list, [a, b, c, d])]


def md5(data: bytes):
    # Padding (bit 1 + n * bit 0)
    # -> ...64B, 56B, 16B (length)

    data = bytearray(data)
    orig_len_in_bits = (8 * len(data)) & 0xffffffffffffffff
    data.append(0x80)

    while len(data) % 64 != 56:  # bit: len(data) = 448 (mod 512)
        data.append(0)

    data += orig_len_in_bits.to_bytes(8, byteorder='little')

    h_list = [A, B, C, D]

    for chunk_ofst in range(0, len(data), 64):
        chunk = list(struct.unpack('<16I', data[chunk_ofst:chunk_ofst + 64]))
        h_list = md5_compress(chunk, h_list)

    # join h (the 4 32-bit words) into a 128-bit hex string
    return sum(x << (32 * i) for i, x in enumerate(h_list)).to_bytes(16, byteorder='little').hex()


input_data = b"hello world"
md5_hash = md5(input_data)
print(md5_hash)
