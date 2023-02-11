from flask import Flask, render_template, request, redirect, url_for
from forms import Todo
from rsa import *
from elGamal import *
from paillier import *
from ecc import *
import sys, os
import ast

app = Flask(__name__)
app.config['SECRET_KEY'] = 'password'

# Output steganography
try:
    os.mkdir("output")
except:
    pass

@app.route('/', methods=['GET', 'POST'])
def main():
    request_method = request.method
    return render_template('index.html',request_method=request_method)


@app.route('/rsa', methods=['GET', 'POST'])
def page_rsa():
    request_method = request.method
    # if len(request.form) == 0:
    #     result = ""
    # else:
    #     if len(request.files.get("srcfile").filename) != 0:
    #         srctext = request.files.get("srcfile").read()
    #         outputfile = "output/rc4-" + request.files.get("srcfile").filename
    #     else:
    #         srctext = request.form.get("message")
    #         outputfile = "output/rc4-manual"


    #     if len(rckey) > 0:
    #         result  = mod_rc4(srctext, rckey)

    #     with open(outputfile, "w") as file:
    #         file.write(str(result.encode('utf-8')))

    # return render_template('rc4.html',request_method=request_method, result=result)\
    return render_template('rsa.html',request_method=request_method)

@app.route('/enc_rsa', methods=['GET', 'POST'])
def enc_rsa():
    request_method = request.method
    n   = int(request.form.get("n"))
    e   = int(request.form.get("e"))
    plainteks   = request.form.get("plainteks")
    res2 = encryptRSA(olahPesanFromKalimat(plainteks),n,e)
    print(res2)
    res = ' '.join([str(elem) for elem in res2])
    return render_template('rsa.html',request_method=request_method, res = res)

@app.route('/dec_rsa', methods=['GET', 'POST'])
def dec_rsa():
    request_method = request.method
    n   = int(request.form.get("n"))
    d   = int(request.form.get("d"))
    cipherteks2   = request.form.get("cipherteks")
    cipherteks = cipherteks2.split(" ")
    res2 = decryptRSA(cipherteks, n, d)
    res3 = (olahPesanToKalimat(res2))
    res = ''.join([str(elem) for elem in res3])
    return render_template('rsa.html',request_method=request_method, res = res.upper())

@app.route('/elgamal', methods=['GET', 'POST'])
def page_elgamal():
    request_method = request.method
    return render_template('elGamal.html',request_method=request_method)

@app.route('/enc_elGamal', methods=['GET', 'POST'])
def enc_elGamal():
    request_method = request.method
    p   = int(request.form.get("p"))
    g   = int(request.form.get("g"))
    x   = int(request.form.get("x"))
    k   = int(request.form.get("k"))
    plainteks   = int(request.form.get("plainteks"))
    publicKey = bangkitKunciElGamal(p,g,x)["public"]
    res = enkripsiElGamal(p,g,x,publicKey,plainteks,k)
    return render_template('elGamal.html',request_method=request_method, res = res)

@app.route('/dec_elGamal', methods=['GET', 'POST'])
def dec_elGamal():
    request_method = request.method
    p   = int(request.form.get("p"))
    g   = int(request.form.get("g"))
    x   = int(request.form.get("x"))
    # cipherteks   = (request.form.get("ciphertext"))
    # cipherteks = cipherteks.replace("(","")
    # cipherteks = cipherteks.replace(")","")
    # cipherteks = cipherteks.split(",")
    ct         = ast.literal_eval(request.form.get("ciphertext"))
    privateKey = bangkitKunciElGamal(p,g,x)["private"]
    # print(cipherteks)
    res = dekripsiElGamal(p,g,x,ct,privateKey)
    # print(res)
    return render_template('elGamal.html',request_method=request_method, res = res)


@app.route('/paillier', methods=['GET', 'POST'])
def page_paillier():
    request_method = request.method
    return render_template('pailier.html',request_method=request_method)

@app.route('/enc_paillier', methods=['GET', 'POST'])
def enc_paillier():
    request_method = request.method
    pt  = int(request.form.get("plainteks"))
    g   = int(request.form.get("g"))
    n   = int(request.form.get("n"))

    res = paillier_enc(pt, (g, n))
    return render_template('pailier.html',request_method=request_method, res=res)

@app.route('/dec_paillier', methods=['GET', 'POST'])
def dec_paillier():
    request_method = request.method
    lam = int(request.form.get("lambda"))
    mu  = int(request.form.get("mu"))
    n   = int(request.form.get("n"))
    ct  = int(request.form.get("cipherteks"))
    res = paillier_dec(ct, n, (lam, mu))
    return render_template('pailier.html',request_method=request_method, res = res)


@app.route('/ecc', methods=['GET', 'POST'])
def page_ecc():
    request_method = request.method
    return render_template('ecc.html',request_method=request_method)


@app.route('/enc_ecc', methods=['GET', 'POST'])
def enc_ecc():
    request_method = request.method
    a      = int(request.form.get("a"))
    b      = int(request.form.get("b"))
    p      = int(request.form.get("p"))
    base_x = int(request.form.get("basex"))
    base_y = int(request.form.get("basey"))

    pub_x  = int(request.form.get("pubx"))
    pub_y  = int(request.form.get("puby"))

    pt     = request.form.get("plainteks")

    enc = ECEG((a, b, p), (base_x, base_y))
    res = str(enc.encrypt(pt, (pub_x, pub_y)))

    return render_template('ecc.html',request_method=request_method, result=res)

@app.route('/dec_ecc', methods=['GET', 'POST'])
def dec_ecc():
    request_method = request.method
    a      = int(request.form.get("a"))
    b      = int(request.form.get("b"))
    p      = int(request.form.get("p"))
    base_x = int(request.form.get("basex"))
    base_y = int(request.form.get("basey"))

    private_key = int(request.form.get("prv_key"))

    ct     = request.form.get("cipherteks")
    ct     = ast.literal_eval(ct)
    enc    = ECEG((a, b, p), (base_x, base_y))
    res    = str(enc.decrypt(ct, private_key))
    print(res, len(res))
    return render_template('ecc.html', request_method=request_method, result=res)



@app.route('/page_keygen', methods=['GET', 'POST'])
def page_keygen():
    request_method = request.method
    return render_template('keygen.html',request_method=request_method)

@app.route('/keygen_rsa', methods=['GET', 'POST'])
def keygen_rsa():
    request_method = request.method

    result = generate_rsa_key()
    return render_template('keygen.html',request_method=request_method, result=result)

@app.route('/keygen_elgamal', methods=['GET', 'POST'])
def keygen_elgamal():
    request_method = request.method

    result = elgamal_keygen()
    return render_template('keygen.html',request_method=request_method, result=result)

@app.route('/keygen_paillier', methods=['GET', 'POST'])
def keygen_paillier():
    request_method = request.method

    result = paillier_keygen()
    return render_template('keygen.html',request_method=request_method, result=result)

@app.route('/keygen_ecc', methods=['GET', 'POST'])
def keygen_ecc():
    request_method = request.method
    a      = int(request.form.get("a"))
    b      = int(request.form.get("b"))
    p      = int(request.form.get("p"))
    base_x = int(request.form.get("basex"))
    base_y = int(request.form.get("basey"))
    enc    = ECEG((a, b, p), (base_x, base_y))

    result = enc.generate_key()
    return render_template('keygen.html',request_method=request_method, result=result)







if __name__ == '__main__':
    app.run(debug=True)
