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

def generate_rsa_key() -> dict:
    p   = get_prime(1 << 31)
    q   = get_prime(1 << 31)

    n   = p * q
    phi = (p - 1) * (q - 1)
    e   = random.randint(2, phi)
    while gcd(phi, e) != 1:
        e   = random.randint(2, phi)

    d   = pow(e, -1, phi)
    return {'p' : p, 'q' : q, 'e' : e, 'd' : d}



def olahPesanFromKalimat(pesan):
    pesan = pesan.strip()
    while len(pesan) % 4 != 0:
        pesan += "X"
    split_strings = [pesan[index : index + 4] for index in range(0, len(pesan), 4)]
    res = []
    for i in range (len(split_strings)):
        temp = []
        for j in range (len(split_strings[i])):
            temp2 = (ord(split_strings[i][j].lower())-97)
            if (temp2 < 10):
                temp3 = "0"+str(temp2)
                temp.append(temp3)
            else:
                temp.append(str(temp2))
        res.append(str(temp[0]+temp[1]))
        if (len(temp) != (4/2)):
            res.append(str(temp[2]+temp[3]))
    return res

# print(olahPesanFromKalimat('HELLOALICE'))

def olahPesanToKalimat(array):
    res = []
    for i in range (len(array)):
        if (len(array[i]) == 3):
            array[i] = array[i][1:]
        res.append(chr(int(array[i][:2])+97))
        res.append(chr(int(array[i][2:])+97))
    return res

def encryptRSA(pesan,n,e):
    m_array = []
    for i in range(len(pesan)):
        temp = pow(int(pesan[i]), int(e) ,int(n))
        if (temp < 1000):
            temp2 = "0"+str(temp)
            m_array.append(temp2)
        else:
            m_array.append(str(temp))
    return(m_array)

def decryptRSA(ciphertext,n,d):
    m_array = []
    for i in range (len(ciphertext)):
        if (ciphertext[i] != ' '):
            temp = pow(int(ciphertext[i]), int(d), int(n))
            if (temp < 1000):
                temp2 = "0"+str(temp)
                m_array.append(temp2)
            else:
                m_array.append(str(temp))
    return(m_array)

# temp = encryptRSA(olahPesanFromKalimat('HELLOALICE'),47,71,79)
# print(temp)
# listToStr = ' '.join([str(elem) for elem in temp])
# temp2 = olahPesanToKalimat(decryptRSA("0328 0301 2653 2986 1164",47,71,generateKunciDekripsi(47,71,79)))
# print(temp2)
# listToStr2 = ''.join([str(elem) for elem in temp2])
# # print(listToStr)
# print(listToStr2)
# print(listToStr)
# # olahPesanToKalimat(olahPesanFromKalimat('HELLOALICE'))
# inputan = ("0328 0301 2653 2986 1164").split(" ")
# ress = (decryptRSA(inputan,47,71,generateKunciDekripsi(47,71,79)))


# te = (olahPesanToKalimat(ress))
# res = ''.join([str(elem) for elem in te])
# print(res.upper())
