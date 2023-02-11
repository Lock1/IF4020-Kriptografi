import struct
import binascii

def pad(src : str) -> bytes:
    # Assuming input normal binary file,
    #   appending bit '1', '10', '100', ..., '1000 000' will never divisible by 512
    #   due normal binary file bit length always divisible by 8 / binary file always accessed in 8 bit (1 byte).
    # Therefore minimum K is 7
    L       = 8*len(src)
    found_k = False
    K       = 0          # Note : This K is offset by 7 from K in SHA2-256 wikipedia documentation
    while not found_k:
        if (L + 1 + (K + 7) + 64) % 512 == 0:
            found_k = True
        else:
            K += 1

    return bytes(src, "ascii") + b"\x80" + struct.pack("x") * (K // 8) + struct.pack(">Q", L)

def slice512(src : bytes) -> list:
    sliced = []
    char_length = 512 // 8
    for i in range(len(src) // char_length):
        sliced.append(src[i*char_length:(i + 1)*char_length])
    return sliced

def rrot(src : int, count : int) -> int:
    # For 32-bit
    shr  = src >> count
    mask = 0
    for i in range(count):
        mask <<= 1
        mask  |= 1

    return shr ^ (mask & src) << (32 - count)

def sha256(src : str) -> str:
    h_const = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]
    k_const = [
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
        0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
        0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
        0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
        0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
        0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
        0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
        0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
    ]
    padded = pad(src)

    for chunk in slice512(padded):
        w = [struct.unpack(">I", chunk[i*4:(i+1)*4])[0] if i < 16 else 0 for i in range(64)]

        for i in range(16, 64):
            s0   = rrot(w[i-15], 7) ^ rrot(w[i-15], 18) ^ (w[i-15] >> 3)
            s1   = rrot(w[i-2], 17) ^ rrot(w[i-2],  19) ^ (w[i-2] >> 10)
            w[i] = (w[i-16] + s0 + w[i-7] + s1) % (1 << 32)

        a, b, c, d, e, f, g, h = h_const

        for i in range(64):
            S1    = rrot(e, 6) ^ rrot(e, 11) ^ rrot(e, 25)
            ch    = (e & f)    ^ ((~e & 0xFFFFFFFF) & g)           # Special treatment for python bitwise not
            temp1 =( h + S1 + ch + k_const[i] + w[i]) % (1 << 32)
            S0    = rrot(a, 2) ^ rrot(a, 13) ^ rrot(a, 22)
            maj   = (a & b) ^ (a & c) ^ (b & c)
            temp2 = (S0 + maj) % (1 << 32)

            h = g
            g = f
            f = e
            e = (d + temp1) % (1 << 32)
            d = c
            c = b
            b = a
            a = (temp1 + temp2) % (1 << 32)

        h_const[0] = (h_const[0] + a) % (1 << 32)
        h_const[1] = (h_const[1] + b) % (1 << 32)
        h_const[2] = (h_const[2] + c) % (1 << 32)
        h_const[3] = (h_const[3] + d) % (1 << 32)
        h_const[4] = (h_const[4] + e) % (1 << 32)
        h_const[5] = (h_const[5] + f) % (1 << 32)
        h_const[6] = (h_const[6] + g) % (1 << 32)
        h_const[7] = (h_const[7] + h) % (1 << 32)

    list_result = [str(binascii.hexlify(struct.pack(">I", a)))[2:10] for a in h_const]
    return "".join(list_result)
