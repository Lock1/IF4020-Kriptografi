import random

def is_prime(p : int, classic=False) -> bool:
    if p % 2 == 0:
        return False

    if classic:
        primality = True
        n = 2
        while primality and n <= int(p**(0.5)):
            if p % n == 0:
                primality = False
            n += 1
        return primality
    else:
        # Specific Miller primality test for 64~ bits
        if p < 3317044064679887385961981:
            temp_calc = p - 1    # Temp variable for calculating s and d
            s         = 0
            while temp_calc > 0 and temp_calc & 0x01 == 0x00:   # Even-ness test using bit operator
                temp_calc >>= 1
                s          += 1
            d = temp_calc
            assert d & 0x01 == 0x01  # Odd-ness test

            a_tests = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41]
            for a in a_tests:
                # First test
                if pow(a, d, p) == 1:
                    return True
                else:
                    # Second test
                    for r in range(s):
                        if pow(a, pow(2, r) * d, p) == (p - 1):   # (p - 1) congruent with -1 (mod p)
                            return True
            return False
        else:
            assert False

def get_prime(upper_bound : int) -> int:
    p = random.randint(2, upper_bound)
    while not is_prime(p):
        p = random.randint(2, upper_bound)
    return p

def gcd(a : int, b : int) -> int:
    if b == 0:
        return a
    return gcd(b, a % b)

def generate_rsa_key(key_length : int = 64) -> dict:
    p   = get_prime(1 << key_length)
    q   = get_prime(1 << key_length)

    n   = p * q
    phi = (p - 1) * (q - 1)
    e   = random.randint(2, phi)
    while gcd(phi, e) != 1:
        e   = random.randint(2, phi)

    d   = pow(e, -1, phi)
    return {'p' : p, 'q' : q, 'e' : e, 'd' : d}





def encryptSignature(h, sk, n) -> int:
    return pow(h, sk, n)

def decryptSignature(s, pk, n) -> int:
    return pow(s, pk, n)
