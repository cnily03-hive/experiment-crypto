# x^15 + x + 1

def LFSRXOR(seed, taps):
    lfsr = seed
    max_tap = max(taps)
    while True:
        yield lfsr & 1
        xor = 0
        for t in taps:
            xor ^= (lfsr >> t) & 1
        lfsr = (lfsr >> 1) | (xor << (max_tap - 1))


def pad_start(s, n):
    return '0' * (n - len(s)) + s

def main():
    seed = 0x5678
    taps = [15, 1, 0]
    lfsr = LFSRXOR(seed, taps)

    f = open('target/output.txt', 'w')
    for n in range(2**15):
        num = 0
        for i in range(15):
            num |= next(lfsr) << i
        f.write(f'{n+1}. ' + pad_start(hex(num)[2:], 4).upper() + '\n')


if __name__ == '__main__':
    main()
