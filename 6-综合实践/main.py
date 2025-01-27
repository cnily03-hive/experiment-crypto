import socket
from Crypto.Util.number import bytes_to_long, long_to_bytes
import argparse
from io import BytesIO
import sys
from base64 import b64decode
import math
import struct

pubkey = 'X9IcwkDZ5RwsGOsZx7IQT9DSAQVVy/lGyn+SzF9AZqmKfMZhfxiWsDm+ihE1lcrcGUP2q73QJd9Zi9N/nqBDQKOBHeLgwqG9Yl06wiNTR6QKupwXBpcRfF+uOWCmcUdcI36o6OhZnrhxOcqparM2aiT7Is8NKoakB+Kq368VAdn+UGDu0TTPjRdNX8NyEoaFLQsEXOJSv67dr62ejX8nWxL65+lnPDeU1ZfJ1O9krluBW1Jo5Vcdf1YoTysuRiBcWfeQvFQOfo5UetnhrzQPxd/PCxBXmoq/Uz3bi0O661bCB5ix6wkH9vPykjRWOHXfFYSI6lEHQsluHOsJpa1YafYJ07LIVoleKf8W261CpPfXcAi7SI4q4uJaiD1vEbYTEyayHzVlUWjIyvZUGY5RHmKoDsdo+0jISDaZ0AshCKB7L9ql4QJstgtmB1GH5418ta9KzpO0obyk+s5Cr06BK9v3Lnvn+vCxpA706QRkL+tVQgj9ahtQsIxe0Hq6EUbQ4oz94zOeR26HLpnn2XXpXz4nQlR5JK/QLX/L254kVhe1/KeF6NsRkgjsVBhZzLYl0Q7LLaxpL/F4PA/ZrUXm5uw9BjmlwIbtldxCKXtOPWdOQWanFAiq4ssM45skAWvwo3Ik1ym10h3MrHwMdpS7WAWav5QP1cRIRbjMurkmNrc='
privkey = 'jvD9iPmfH6UxRIvHeGAK971w6l3UmcW7f1F61stZAXS18JXya8H4Y1nW72LFN6A/wAK0tn+S2kt0GPlHYCAwadQLC+LxyeRGehnQCXmhtAL9qZhxTCyJvzX3dFW77V4lNThdVgGwOqGZ5x981Dht9qTNDVr4NpcYX9ih5p9Q8IkxR2z0i7nibCpwMVDJpwTJHI2SU50PMKpsCL8zBR4UypzvAh2ITbUg+s6AngJ2mQSItrAF9LXQZnnNiuv4XddUbu41e31CQb26b3mcSzGcFY5iRajXwU1+M5WQYkiDwOFgRnSuZSTNlQB0+R+Qh8tAePCrEfoGSpwpmn4u7BkpefYJ07LIVoleKf8W261CpPfXcAi7SI4q4uJaiD1vEbYTEyayHzVlUWjIyvZUGY5RHmKoDsdo+0jISDaZ0AshCKB7L9ql4QJstgtmB1GH5418ta9KzpO0obyk+s5Cr06BK9v3Lnvn+vCxpA706QRkL+tVQgj9ahtQsIxe0Hq6EUbQ4oz94zOeR26HLpnn2XXpXz4nQlR5JK/QLX/L254kVhe1/KeF6NsRkgjsVBhZzLYl0Q7LLaxpL/F4PA/ZrUXm5uw9BjmlwIbtldxCKXtOPWdOQWanFAiq4ssM45skAWvwo3Ik1ym10h3MrHwMdpS7WAWav5QP1cRIRbjMurkmNrc='


def decode_key(key: str):
    key = b64decode(key)
    key = bytes_to_long(key)
    a = key >> 2048
    b = key & ((1 << 2048) - 1)
    return a, b


def encrypt(data: bytes, e, n) -> bytes:
    m = bytes_to_long(data)
    c = pow(m, e, n)
    return long_to_bytes(c)


def decrypt(data: bytes, d, n) -> bytes:
    c = bytes_to_long(data)
    m = pow(c, d, n)
    return long_to_bytes(m)


def send_data(s: socket, reader: BytesIO, e, n):
    while True:
        chunk = reader.read(math.ceil(n.bit_length() / 8))
        if not chunk:
            break
        s.send(encrypt(chunk, e, n))


def recv_data(s: socket, writer: BytesIO, d, n):
    sock, addr = s.accept()
    while True:
        try:
            chunk = sock.recv(math.ceil(n.bit_length() / 8))
            if not chunk:
                break
            writer.write(decrypt(chunk, d, n))
            writer.flush()
        except KeyboardInterrupt:
            break


if __name__ == '__main__':
    # xxx send xxx:xxx [--data xxx] [--file xxx]
    # xxx recv xxx [--output xxx]
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='action')
    send_parser = subparsers.add_parser('send')
    send_parser.add_argument('dest')
    send_parser.add_argument('--data', '-d')
    send_parser.add_argument('--file', '-f')
    recv_parser = subparsers.add_parser('recv')
    recv_parser.add_argument('dest')
    recv_parser.add_argument('--output', '-o')
    args = parser.parse_args()

    if args.action == 'send':
        reader = None
        if args.file:
            reader = open(args.file, 'rb')
        else:
            reader = BytesIO(args.data.encode())
        dest = args.dest
        host, port = dest.split(':')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        e, n = decode_key(pubkey)
        s.connect((host, int(port)))
        send_data(s, reader, e, n)
        s.send(b'')
        s.close()

    elif args.action == 'recv':
        outfile = args.output if args.output else None
        if outfile:
            writer = open(outfile, 'wb')
        else:
            writer = sys.stdout.buffer

        dest = args.dest
        if ':' not in dest:
            dest = ":" + dest
        host, port = dest.split(':')
        if host == '':
            host = '0.0.0.0'
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, int(port)))

        d, n = decode_key(privkey)
        s.listen(1)
        recv_data(s, writer, d, n)
        s.close()

    else:
        parser.print_help()
        sys.exit(1)
