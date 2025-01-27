import math


class SM3:
    IV = [0x7380166f, 0x4914b2b9, 0x172442d7, 0xda8a0600,
          0xa96f30bc, 0x163138aa, 0xe38dee4d, 0xb0fb0e4e]

    @staticmethod
    def out_hex(list1):
        for i in list1:
            print("%08x" % i)
        print("\n")

    @staticmethod
    def left_rotate(a, k):
        k = k % 32
        return ((a << k) & 0xFFFFFFFF) | ((a & 0xFFFFFFFF) >> (32 - k))

    T_j = []
    for i in range(0, 16):
        T_j.append(0)
        T_j[i] = 0x79cc4519
    for i in range(16, 64):
        T_j.append(0)
        T_j[i] = 0x7a879d8a

    @staticmethod
    def FF_j(X, Y, Z, j):
        if 0 <= j and j < 16:
            ret = X ^ Y ^ Z
        elif 16 <= j and j < 64:
            ret = (X & Y) | (X & Z) | (Y & Z)
        return ret

    @staticmethod
    def GG_j(X, Y, Z, j):
        if 0 <= j and j < 16:
            ret = X ^ Y ^ Z
        elif 16 <= j and j < 64:
            # ret = (X | Y) & ((2 ** 32 - 1 - X) | Z)
            ret = (X & Y) | ((~ X) & Z)
        return ret

    @staticmethod
    def P_0(X):
        return X ^ (SM3.left_rotate(X, 9)) ^ (SM3.left_rotate(X, 17))

    @staticmethod
    def P_1(X):
        return X ^ (SM3.left_rotate(X, 15)) ^ (SM3.left_rotate(X, 23))

    @staticmethod
    def CF(V_i, B_i):
        W = []
        for i in range(16):
            weight = 0x1000000
            data = 0
            for k in range(i * 4, (i + 1) * 4):
                data = data + B_i[k] * weight
                weight = int(weight / 0x100)
            W.append(data)

        for j in range(16, 68):
            W.append(0)
            W[j] = SM3.P_1(W[j - 16] ^ W[j - 9] ^ (SM3.left_rotate(W[j - 3], 15))
                           ) ^ (SM3.left_rotate(W[j - 13], 7)) ^ W[j - 6]
            str1 = "%08x" % W[j]
        W_1 = []
        for j in range(0, 64):
            W_1.append(0)
            W_1[j] = W[j] ^ W[j + 4]
            str1 = "%08x" % W_1[j]

        A, B, C, D, E, F, G, H = V_i
        """
        print "00",
        out_hex([A, B, C, D, E, F, G, H])
        """
        for j in range(0, 64):
            SS1 = SM3.left_rotate(
                ((SM3.left_rotate(A, 12)) + E + (SM3.left_rotate(SM3.T_j[j], j))) & 0xFFFFFFFF, 7)
            SS2 = SS1 ^ (SM3.left_rotate(A, 12))
            TT1 = (SM3.FF_j(A, B, C, j) + D + SS2 + W_1[j]) & 0xFFFFFFFF
            TT2 = (SM3.GG_j(E, F, G, j) + H + SS1 + W[j]) & 0xFFFFFFFF
            D = C
            C = SM3.left_rotate(B, 9)
            B = A
            A = TT1
            H = G
            G = SM3.left_rotate(F, 19)
            F = E
            E = SM3.P_0(TT2)

            A = A & 0xFFFFFFFF
            B = B & 0xFFFFFFFF
            C = C & 0xFFFFFFFF
            D = D & 0xFFFFFFFF
            E = E & 0xFFFFFFFF
            F = F & 0xFFFFFFFF
            G = G & 0xFFFFFFFF
            H = H & 0xFFFFFFFF

        V_i_1 = []
        V_i_1.append(A ^ V_i[0])
        V_i_1.append(B ^ V_i[1])
        V_i_1.append(C ^ V_i[2])
        V_i_1.append(D ^ V_i[3])
        V_i_1.append(E ^ V_i[4])
        V_i_1.append(F ^ V_i[5])
        V_i_1.append(G ^ V_i[6])
        V_i_1.append(H ^ V_i[7])
        return V_i_1

    @staticmethod
    def hash_msg(msg):
        # print(msg)
        len1 = len(msg)
        reserve1 = len1 % 64
        msg.append(0x80)
        reserve1 = reserve1 + 1
        # 56-64, add 64 byte
        range_end = 56
        if reserve1 > range_end:
            range_end = range_end + 64

        for i in range(reserve1, range_end):
            msg.append(0x00)

        bit_length = (len1) * 8
        bit_length_str = [bit_length % 0x100]
        for i in range(7):
            bit_length = int(bit_length / 0x100)
            bit_length_str.append(bit_length % 0x100)
        for i in range(8):
            msg.append(bit_length_str[7 - i])

        # print(msg)

        group_count = round(len(msg) / 64)

        B = []
        for i in range(0, group_count):
            B.append(msg[i * 64:(i + 1) * 64])

        V = []
        V.append(SM3.IV)
        for i in range(0, group_count):
            V.append(SM3.CF(V[i], B[i]))

        y = V[i + 1]
        result = ""
        for i in y:
            result = '%s%08x' % (result, i)
        return result

    @staticmethod
    def str2byte(msg):  # 字符串转换成byte数组
        ml = len(msg)
        msg_byte = []
        msg_bytearray = msg  # 如果加密对象是字符串，则在此对msg做encode()编码即可，否则不编码
        for i in range(ml):
            msg_byte.append(msg_bytearray[i])
        return msg_byte

    @staticmethod
    def byte2str(msg):  # byte数组转字符串
        ml = len(msg)
        str1 = b""
        for i in range(ml):
            str1 += b'%c' % msg[i]
        return str1.decode('utf-8')

    @staticmethod
    def hex2byte(msg):  # 16进制字符串转换成byte数组
        ml = len(msg)
        if ml % 2 != 0:
            msg = '0' + msg
        ml = int(len(msg) / 2)
        msg_byte = []
        for i in range(ml):
            msg_byte.append(int(msg[i * 2:i * 2 + 2], 16))
        return msg_byte

    @staticmethod
    def byte2hex(msg):  # byte数组转换成16进制字符串
        ml = len(msg)
        hexstr = ""
        for i in range(ml):
            hexstr = hexstr + ('%02x' % msg[i])
        return hexstr

    @staticmethod
    def KDF(Z, klen):  # Z为16进制表示的比特串（str），klen为密钥长度（单位byte）
        klen = int(klen)
        ct = 0x00000001
        rcnt = math.ceil(klen / 32)
        Zin = SM3.hex2byte(Z)
        Ha = ""
        for i in range(int(rcnt)):
            msg = Zin + SM3.hex2byte('%08x' % ct)
            # print(msg)
            Ha = Ha + SM3.hash_msg(msg)
            # print(Ha)
            ct += 1
        return Ha[0: klen * 2]

    @classmethod
    def encryptSM3(cls, msg, Hexstr=0):
        if (Hexstr):
            msg_byte = SM3.hex2byte(msg.encode())
        else:
            msg_byte = SM3.str2byte(msg.encode())
        return SM3.hash_msg(msg_byte)


if __name__ == '__main__':
    print(SM3.encryptSM3('hello world'))
