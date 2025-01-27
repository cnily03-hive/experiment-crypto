import string
from collections import Counter

english_freq = {
    'a': 0.08167, 'b': 0.01492, 'c': 0.02782, 'd': 0.04253, 'e': 0.12702, 'f': 0.02228, 'g': 0.02015,
    'h': 0.06094, 'i': 0.06966, 'j': 0.00153, 'k': 0.00772, 'l': 0.04025, 'm': 0.02406, 'n': 0.06749,
    'o': 0.07507, 'p': 0.01929, 'q': 0.00095, 'r': 0.05987, 's': 0.06327, 't': 0.09056, 'u': 0.02758,
    'v': 0.00978, 'w': 0.02360, 'x': 0.00150, 'y': 0.01974, 'z': 0.00074
}


def calc_ic(text):
    N = len(text)
    freq = Counter(text)
    ic = sum(f * (f - 1) for f in freq.values()) / (N * (N - 1))
    return ic


def shift_letter(letter, shift, is_upper=False):
    base = ord('A') if is_upper else ord('a')
    return chr((ord(letter) - base + shift) % 26 + base)


def decrypt_vigenere(ciphertext, key):
    key_len = len(key)
    plaintext = []
    key_index = 0
    for char in ciphertext:
        if char.isalpha():
            shift = ord(key[key_index].lower()) - ord('a')
            plaintext.append(shift_letter(char, -shift, char.isupper()))
            key_index = (key_index + 1) % key_len
        else:
            plaintext.append(char)
    return ''.join(plaintext)


def guess_key_length(ciphertext, in_range=range(1, 21)):
    ciphertext = ciphertext.lower()
    best_ic = 0
    best_length = 0
    for length in in_range:
        substrings = [''] * length
        for i, char in enumerate(ciphertext):
            if char.isalpha():
                substrings[i % length] += char.lower()

        avg_ic = 0
        for substring in substrings:
            avg_ic += calc_ic(substring)
        avg_ic /= length

        if abs(avg_ic - 0.068) < abs(best_ic - 0.068):
            best_ic = avg_ic
            best_length = length

    return best_length


def break_vigenere_key(ciphertext, keylen):
    ciphertext = ciphertext.lower()
    key_length = keylen

    substrings = [''] * key_length
    for i, char in enumerate(ciphertext):
        if char.isalpha():
            substrings[i % key_length] += char

    key = []
    for substring in substrings:
        max_score = -float('inf')
        best_shift = 0
        for shift in range(26):
            decrypted = ''.join(shift_letter(c, -shift) for c in substring)
            score = sum([decrypted.count(letter) * english_freq.get(letter, 0)
                         for letter in string.ascii_lowercase])
            if score > max_score:
                max_score = score
                best_shift = shift
        key.append(chr(best_shift + ord('A')))

    key = ''.join(key)
    return key


ciphertext = "CHREEVOAHMAERATBIAXXWTNXBEEOPHBSBQMQEQERBWRVXUOAKXAOSXXWEAHBWGJMMQMNKGRFVGXWTRZXWIAKLXFPSKAUTEMNDCMGTSXMXBTUIADNGMGPSRELXNJELXVRVPRTULHDNQWTWDTYGBPHXTFALJHASVBFXNGLLCHRZBWELEKMSJIKNBHWRJGNMGJSGLXFEYPHAGNRBIEQJTAMRVLCRREMNDGLXRRIMGNSNRWCHRQHAEYEVTAQEBBIPEEWEVKAKOEWADREMXMTBHHCHRTKDNVRZCHRCLQOHPWQAIIWXNRMGWOIIFKEE"

key_length = guess_key_length(ciphertext)
print(f"\033[34mEstimated key length:\033[0m {key_length}")
key = break_vigenere_key(ciphertext, keylen=key_length)
print(f"\033[34mGuessed key:\033[0m {key}")
plaintext = decrypt_vigenere(ciphertext, key)
print(plaintext)
