def left_rotate(n, b):
    return ((n << b) & 0xFFFFFFFF) | (n >> (32 - b))


def sha1(message: bytes) -> bytes:

    # initial hash values
    H0 = 0x67452301
    H1 = 0xEFCDAB89
    H2 = 0x98BADCFE
    H3 = 0x10325476
    H4 = 0xC3D2E1F0

    msg_bit_len = len(message) * 8

    message = bytearray(message)

    # pad
    message.append(0x80)
    while len(message) % 64 != 56:
        message.append(0x00)

    message += msg_bit_len.to_bytes(8, byteorder='big')

    # chunk
    for i in range(0, len(message), 64):
        block = message[i:i + 64]

        # split to 16 32-bit words
        w = [0] * 80
        for j in range(16):
            w[j] = int.from_bytes(block[j*4:j*4+4], byteorder='big')

        # extend to 80 32-bit words
        for j in range(16, 80):
            w[j] = left_rotate(w[j-3] ^ w[j-8] ^ w[j-14] ^ w[j-16], 1)

        # init the hash buffer
        a, b, c, d, e = H0, H1, H2, H3, H4

        # 80 turns iteration
        for j in range(80):
            if 0 <= j <= 19:
                f = (b & c) | (~b & d)
                k = 0x5A827999
            elif 20 <= j <= 39:
                f = b ^ c ^ d
                k = 0x6ED9EBA1
            elif 40 <= j <= 59:
                f = (b & c) | (b & d) | (c & d)
                k = 0x8F1BBCDC
            else:
                f = b ^ c ^ d
                k = 0xCA62C1D6

            temp = (left_rotate(a, 5) + f + e + k + w[j]) & 0xFFFFFFFF
            e = d
            d = c
            c = left_rotate(b, 30)
            b = a
            a = temp

        # update the hash buffer
        H0 = (H0 + a) & 0xFFFFFFFF
        H1 = (H1 + b) & 0xFFFFFFFF
        H2 = (H2 + c) & 0xFFFFFFFF
        H3 = (H3 + d) & 0xFFFFFFFF
        H4 = (H4 + e) & 0xFFFFFFFF

    return b''.join([x.to_bytes(4, byteorder='big') for x in (H0, H1, H2, H3, H4)])

def byte_to_hex(byte_str):
    return ''.join(f'{x:02x}' for x in byte_str)

message = b"hello world!"
hash = byte_to_hex(sha1(message))
print(hash)
