import random
from math import inf

CONSTANT_O = (0, inf)

class ECC:
    def __init__(self, curve_coef : (int, int, int), base : (int, int)):
        # Elliptic curve : y^2 = x^3 + ax + b (mod p)
        self.coef   = curve_coef   # Tuple (a, b, p)
        self.base   = base         # ECC base point
        self.points = self.__generate_points()

    def __generate_points(self) -> list:
        a, b, p = self.coef
        domain  = []

        for x in range(p):
            for y in range(p):
                if (y**2) % p == (x**3 + a*x + b) % p:
                    domain.append((x, y))

        return domain

    def __valid_point(self, point : (int, int)) -> bool:
        if point == CONSTANT_O:
            return True
        else:
            return (point[1]**2) % self.coef[2] == (point[0]**3 + self.coef[0] * point[0] + self.coef[1]) % self.coef[2]

    def add(self, pointA : (int, int), pointB : (int, int)) -> (int, int):
        assert self.__valid_point(pointA) and self.__valid_point(pointB)

        a, b, p = self.coef
        xp, yp  = pointA
        xq, yq  = pointB

        if xp == xq and -yp == yq:
            # Edge case : Inverse
            # P + (-P) = O
            return CONSTANT_O
        else:
            if xp == xq and yp == yq:
                # Edge case : Tangent
                # P + P = R
                m  = ((3*xp**2 + a) * pow(2*yp, -1, p)) % p
            elif xp == xq:
                # Edge case : Tangent but yp = 0
                return CONSTANT_O
            elif pointA == CONSTANT_O:
                # Edge case : Adding O + B
                return pointB
            elif pointB == CONSTANT_O:
                # Edge case : Adding A + O
                return pointA
            else:
                # General case
                # P + Q = R
                # m = (yp - yq)/(xp - xq) mod p
                m  = ((yp - yq) * pow(xp - xq, -1, p)) % p
            xr = (m**2 - xp - xq) % p
            yr = (m * (xp - xr) - yp) % p

        return (xr, yr)

    def multiply(self, point : (int, int), k : int) -> (int, int):
        assert self.__valid_point(point)
        result = point
        for _ in range(k - 1):
            result = self.add(result, point)
        return result

    def negate(self, point : (int, int)) -> (int, int):
        return (point[0], -point[1])

    def generate_key(self) -> dict:
        x = random.randint(1, self.coef[2] - 1)
        q = self.multiply(self.base, x)
        return {'private' : x, 'public' : q}

    def get_random_point(self) -> (int, int):
        return random.choice(self.map)



class ECEG(ECC):
    def __init__(self, curve_coef : (int, int, int), base : (int, int)):
        super(ECEG, self).__init__(curve_coef, base)
        self.__generate_encoding_map()

    def __generate_encoding_map(self):
        # Using simple encoding
        chr_map = {}
        inv_map = {}
        map_ctr = 0
        for c in [chr(0x41 + i) for i in range(26)]:
            if len(self.points) > map_ctr:
                chr_map[c] = self.points[map_ctr]
                inv_map[self.points[map_ctr]] = c
            map_ctr   += 1
        self.map    = chr_map
        self.invmap = inv_map

    def __enc_chr(self, pt : (int, int), pub_key : (int, int)) -> tuple:
        a, b, p = self.coef

        k      = random.randint(1, p-1)
        point1 = self.multiply(self.base, k)
        point2 = self.add(pt, self.multiply(pub_key, k))
        return (point1, point2)

    def __dec_chr(self, enc_points : tuple, priv_key : int) -> (int, int):
        priv_point = self.multiply(enc_points[0], priv_key)
        priv_point = self.negate(priv_point)
        return self.add(enc_points[1], priv_point)

    def encrypt(self, pt : str, public_key : (int, int)) -> tuple:
        # Assuming elliptic curve point count >= 26
        #    or message is encodable for count < 26
        pt         = pt.upper()
        cipher_set = []
        for c in pt:
            c_points = self.__enc_chr(self.map[c], public_key)
            cipher_set.append(c_points)

        return cipher_set

    def decrypt(self, cipher_set : tuple, private_key : int) -> str:
        pt = ""
        for points in cipher_set:
            pt += self.invmap[self.__dec_chr(points, private_key)]

        return pt


# ECC test
# coef     = (1, 6, 11)
# base     = (0, 0)
# ecc_test = ECC(coef, base)
# print(ecc_test.add((2, 4), (5, 9)))
# print(ecc_test.multiply((2, 4), 2))

# ECEG test
# coef     = (-1, 188, 751)
# base     = (201, 5)
# ecc_test = ECEG(coef, base)
# # print(ecc_test.generate_key())
# # {'private': 473, 'public': (479, 355)}
# # {'private': 176, 'public': (603, 587)}
# print(ecc_test.encrypt("HEHEHAHA", (479, 355)))
# tpl = [((169, 132), (386, 679)), ((384, 306), (232, 701)), ((295, 110), (34, 633)), ((198, 322), (701, 548)), ((731, 529), (701, 203)), ((329, 382), (485, 13)), ((385, 328), (44, 439)), ((211, 731), (229, 115))]
# tpl = [((207, 536), (514, 550)), ((231, 575), (687, 244)), ((487, 380), (352, 686)), ((283, 54), (266, 507)), ((332, 50), (214, 675)), ((124, 354), (412, 560)), ((717, 150), (695, 581)), ((248, 515), (589, 672))]
# print(ecc_test.decrypt(tpl, 473))
