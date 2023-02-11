from flask import Flask, render_template, request, redirect, url_for
from forms import Todo
from steganography import *
from modified_rc4 import *
import sys, os

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


@app.route('/rc4', methods=['GET', 'POST'])
def page_rc4():
    request_method = request.method
    if len(request.form) == 0:
        result = ""
    else:
        if len(request.files.get("srcfile").filename) != 0:
            srctext = request.files.get("srcfile").read()
            outputfile = "output/rc4-" + request.files.get("srcfile").filename
        else:
            srctext = request.form.get("message")
            outputfile = "output/rc4-manual"

        rckey   = request.form.get("key")
        if len(rckey) > 0:
            result  = mod_rc4(srctext, rckey)

        with open(outputfile, "w") as file:
            file.write(result)

    return render_template('rc4.html',request_method=request_method, result=result)

@app.route('/stegano', methods=['GET', 'POST'])
def page_stegano():
    request_method = request.method
    return render_template('stegano.html',request_method=request_method)

@app.route('/fidelity', methods=['GET', 'POST'])
def page_fidelity():
    request_method = request.method
    fidelity       = None

    if len(request.files) > 0:
        cover = request.files.get("cover")
        stego = request.files.get("stego")

        if cover.filename.split(".")[1] == "png":
            fidelity = psnr(cover, stego)
        elif cover.filename.split(".")[1] == "wav":
            fidelity = audiopsnr(cover, stego)

    return render_template('fidelity.html',request_method=request_method, fidelity=fidelity)



@app.route('/enc_stegano', methods=['GET', 'POST'])
def encode_stegano():
    srcfilename = request.files.get("cover-file").filename

    filestream  = request.files.get("cover-file")
    outputfile  = "output/steg-" + srcfilename
    if request.form.get("key") == "":
        stegoKey = None
    else:
        stegoKey = request.form.get("key")

    embedfilestream = request.files.get("embed-file")
    embeddedmsg     = embedfilestream.read()

    stegoEnc = request.form.get("metode-steg")
    if stegoEnc == "with-enc" and len(stegoKey) > 0:
        embeddedmsg = mod_rc4(embeddedmsg, stegoKey)

    if srcfilename.split(".")[1] == "png":
        stegEncoder = StegPNG(filestream, outputfile)
    elif srcfilename.split(".")[1] == "wav":
        stegEncoder = StegWAV(filestream, outputfile)

    stegEncoder.encode(embeddedmsg, stegoKey)

    return redirect('/stegano')

@app.route('/dec_stegano', methods=['GET', 'POST'])
def decode_stegano():
    srcfilename = request.files.get("file").filename.split(".")

    filestream  = request.files.get("file")
    outputfile  = "output/dec-" + srcfilename[0] + ".txt"
    if request.form.get("key") == "":
        stegoKey = None
    else:
        stegoKey = request.form.get("key")

    if srcfilename[1] == "png":
        stegDecoder = StegPNG(filestream, outputfile)
    elif srcfilename[1] == "wav":
        stegDecoder = StegWAV(filestream, outputfile)

    try:
        stegDecoder.decode()
    except:
        # Objek bukan stego object yang valid / lcg header salah
        # TODO : Handler ?
        pass

    return redirect('/stegano')


if __name__ == '__main__':
    app.run(debug=True)
