from . import rsa, sha256

def strip_sign_tag(src : str) -> str:
    # Also stripping \n in signature (-1 in index)
    ds_tag_index = src.rfind("<ds>")
    if ds_tag_index != -1:
        return src[:ds_tag_index-1]
    else:
        return src

def get_digital_sign(src : str) -> int:
    ds_tag_index = src.rfind("<ds>")
    if ds_tag_index != -1:
        ds_closing_tag_index = src.rfind("</ds>")
        return int(src[ds_tag_index+4:ds_closing_tag_index], 16)
    else:
        return -1


def digital_signature_rsa(src : str, private_key : tuple) -> str:
    sk, n = private_key
    hash  = int(sha256.sha256(strip_sign_tag(src)), 16)
    return src + f"\n<ds>{hex(rsa.encryptSignature(hash, sk, n))[2:]}</ds>"

def verify_digisign_rsa(src : str, public_key : tuple) -> bool:
    pk, n   = public_key
    hash    = int(sha256.sha256(strip_sign_tag(src)), 16)
    h_prime = rsa.decryptSignature(get_digital_sign(src), pk, n)
    return h_prime == hash % n
