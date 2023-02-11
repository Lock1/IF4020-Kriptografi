import lib.digisign, lib.rsa, lib.sha256

def interface():
    while True:
        print("-- Digital signature --")
        print("1. Generate RSA key")
        print("2. Generate digital signature")
        print("3. Verify digital signature")

        user_inp = int(input(">> "))

        if user_inp == 1:
            dict_key = lib.rsa.generate_rsa_key()
            print(f"n           = {dict_key['p']*dict_key['q']}")
            print(f"Public key  = {dict_key['e']}")
            print(f"Private key = {dict_key['d']}\n")

        elif user_inp == 2:
            filename = input("Filename without extension = ")
            with open(filename + ".txt", "r") as source:
                user_inp = ""
                print("Auto generate key? (y/n)")
                while user_inp not in ["y", "n"]:
                    user_inp = input(">> ")

                if user_inp == "y":
                    dict_key   = lib.rsa.generate_rsa_key()
                    n          = dict_key["p"] * dict_key["q"]
                    d          = dict_key["d"]
                    e          = dict_key["e"]
                    print(f"Auto private key = {d}")
                    print(f"Auto public key  = {e}")
                    print(f"Auto n           = {n}\n")
                else:
                    d = int(input("Private Key = "))
                    n = int(input("n           = "))

                signed_src = lib.digisign.digital_signature_rsa(source.read(), (d, n))
                with open(filename + "_signed.txt", "w") as dest:
                    dest.write(signed_src)

        elif user_inp == 3:
            filename = input("Filename without extension = ")
            with open(filename + ".txt", "r") as source:
                e    = int(input("Public Key = "))
                n    = int(input("n          = "))
                data = source.read()
                print(f"\nDocument digital signature = {hex(lib.digisign.get_digital_sign(data))[2:]}")
                print(f"Document hash              = {lib.sha256.sha256(lib.digisign.strip_sign_tag(data))}")
                if lib.digisign.verify_digisign_rsa(data, (e, n)):
                    print("Digital signature valid!\n")
                else:
                    print("Warning : Digital signature invalid\n")

if __name__ == '__main__':
    interface()
