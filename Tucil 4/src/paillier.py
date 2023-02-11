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


def paillier_keygen() -> dict:
    valid_primes = False
    while not valid_primes:
        p = get_prime(1 << 16)
        q = get_prime(1 << 16)
        n = p*q
        phi = (p - 1)*(q - 1)
        if gcd(n, phi) == 1:
            valid_primes = True

    lcm = phi // gcd(p - 1, q - 1)
    g   = random.randint(1, n**2 - 1)

    x    = pow(g, lcm, n**2)
    l_mu = (x - 1) // n
    mu   = pow(l_mu, -1, n)

    return {'private' : (lcm, mu), 'public' : (g, n)}


def paillier_enc(pt : int, pb_key : (int, int)) -> int:
    assert 0 <= pt < pb_key[1]

    r = random.randint(1, pb_key[1] - 1)
    while gcd(r, pb_key[1]) != 1:
        r = random.randint(1, pb_key[1] - 1)

    n  = pb_key[1]
    ct = pow(pb_key[0], pt, n**2) * pow(r, pb_key[1], n**2)
    ct = ct % (n**2)
    return ct

def paillier_dec(ct : int, n : int, pr_key : (int, int)) -> int:
    x   = pow(ct, pr_key[0], n**2)
    l_m = (x - 1) // n
    return (l_m * pr_key[1]) % n
