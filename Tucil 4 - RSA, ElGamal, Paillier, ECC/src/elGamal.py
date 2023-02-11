# EL_GAMAL
# 1. Bilangan prima, p (tidak rahasia)
# 2. Bilangan acak, g ( g < p) (tidak rahasia)
# 3. Bilangan acak, x (x < p) (rahasia, kunci privat)
# 4. y = g
# x mod p (tidak rahasia, kunci publik)
# 5. m (plainteks) (rahasia)
# 6. a dan b (cipherteks) (tidak rahasia)

# pilih p
# pilih g dan x
# dengan syarat g < p dan 1 <= x <= p-2
# y = g^x mod p

# Hasil dari algoritma ini:
# - Kunci publik: tripel (y, g, p)
# - Kunci privat: pasangan (x, p)

# proses enkripsi
# susun pesan jadi blok, setiap pesan kurang dari p-1
# pilih k, 1 <= k <= p-2
# a = g^k mod p
# b = y^k m mod p

# proses dekripsi
# pakai x, (a^x)^-1 = a^(p-1-x) mod p
# m = b/(a^x) mod p

# p = 2357
# g = 2
# x = 1751
# m = 2035
# k = 1520

import random

def is_prime(p : int) -> bool:
    primality = True
    n = 2
    while primality and n <= int(p**(0.5)):
        if p % n == 0:
            primality = False
        n += 1
    return primality

def get_prime(upper_bound : int) -> int:
    p = random.randint(2, upper_bound)
    while not is_prime(p):
        p = random.randint(2, upper_bound)
    return p

def gcd(a : int, b : int) -> int:
    if b == 0:
        return a
    return gcd(b, a % b)

def elgamal_keygen() -> dict:
    p = get_prime(1 << 16)

    g = random.randint(1, p - 1)
    x = random.randint(1, p - 2)
    y = pow(g, x, p)

    return {'private' : (x, p), 'public' : (y, g, p)}

def bangkitKunciElGamal(p,g,x):
    y = pow(g,x,p)
    key = {
        "public":[y,g,p],
        "private":[x,p]
    }
    return key

# print(bangkitKunciElGamal(p,g,x)["private"])

def enkripsiElGamal(p,g,x,keyPublic,m,k):
    p = keyPublic[2]
    g = keyPublic[1]
    y = keyPublic[0]
    if (0 <= m and m <= p-1):
        if ( 0 <= k and k <= p-1):
            a = pow(g,k,p)
            b = y ** k * m % p
    return a,b

# kunci = bangkitKunciElGamal(p,g,x)
# ciphertext = enkripsiElGamal(p,g,x,kunci["public"],m,k)
# print(ciphertext)

def dekripsiElGamal(p,g,x,ciphertext,keyPrivate):
    a = int(ciphertext[0])
    b = int(ciphertext[1])
    # untuk 1/a^x
    seperAx = pow(a,(p-1-x),p)
    m = b * seperAx % p
    return m

# print(dekripsiElGamal(p,g,x,['1430', ' 697'],kunci["private"]))
