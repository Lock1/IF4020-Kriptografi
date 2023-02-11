import PIL.Image
from math import log
import numpy as np
import wave

class Steg:
    def __init__(self):
        pass

    def payloadToStegBinary(self, payload : str) -> str:
        result = ""
        if type(payload[0]) == str:
            for c in payload:
                result += bin(ord(c))[2:].zfill(8)
        else:
            for c in payload:
                result += bin(c)[2:].zfill(8)
        return result

    def lcg(self, a : int, b: int, m : int, n : int):
        if a == 0 and b == 0:
            raise Exception("Invalid Value")

        if m is None:
            i = n
            while True:
                yield (a*i + b)
                i += 1
        else:
            # 3 pixel / 8 bits audio pertama reserved sebagai header
            available = [j for j in range(n, m-1)]

            # Swap
            ln = len(available)
            for i in range(0, b << 4, 2):
                g1 = (a*i + b) % ln
                g2 = (ln - a - b*(i+1)) % ln
                available[g1], available[g2] = available[g2], available[g1]

            a_idx = 0
            while True and a_idx < len(available):
                yield available[a_idx]
                a_idx += 1



class StegPNG(Steg):
    def __init__(self, input : "str/fp", output : str):
        self.srcImage       = PIL.Image.open(input)
        self.srcPixels      = self.srcImage.load()
        self.outputName     = output
        self.pixelCount     = self.srcImage.size[0] * self.srcImage.size[1]
        self.maxPayloadSize = self.pixelCount * 3 // 8

    def encode(self, payload : str, key : str = None) -> bool:
        if self.maxPayloadSize < len(payload):
            return False

        # LSB wiping
        for i in range(self.pixelCount):
            x = i %  self.srcImage.size[0]
            y = i // self.srcImage.size[0]
            self.srcPixels[x, y] = (
                (self.srcPixels[x, y][0] & 0xFE),
                (self.srcPixels[x, y][1] & 0xFE),
                (self.srcPixels[x, y][2] & 0xFE)
                )

        # Payload processing
        stegpayload = self.payloadToStegBinary(payload)
        # Padding
        while len(stegpayload) % 3 != 0:
            stegpayload += "0"
        if key is None:
            indexgenerator = self.lcg(1, 0, None, 3)
            stegheader    = "001000000"
        else:
            # 3 bit for a, 6 bit for b
            a = ord(key[0]) % 8
            b = sum([ord(c) for c in key]) % 64
            if b == 0:
                b = 1
            indexgenerator = self.lcg(a, b, self.pixelCount, 3)
            stegheader     = bin(a)[2:].zfill(3) + bin(b)[2:].zfill(6)

        # Insertion
        for i in range(3):
            self.srcPixels[i, 0] = (
                (self.srcPixels[i, 0][0] & 0xFE) | int(stegheader[3*i]),
                (self.srcPixels[i, 0][1] & 0xFE) | int(stegheader[3*i+1]),
                (self.srcPixels[i, 0][2] & 0xFE) | int(stegheader[3*i+2])
                )

        img_idx = next(indexgenerator)
        for i in range(0, len(stegpayload), 3):
            x = img_idx %  self.srcImage.size[0]
            y = img_idx // self.srcImage.size[0]
            img_idx = next(indexgenerator)
            self.srcPixels[x, y] = (
                (self.srcPixels[x, y][0] & 0xFE) | int(stegpayload[i]),
                (self.srcPixels[x, y][1] & 0xFE) | int(stegpayload[i+1]),
                (self.srcPixels[x, y][2] & 0xFE) | int(stegpayload[i+2])
                )

        self.srcImage.save(self.outputName)
        return True

    def decode(self):
        resultbin = ""

        stegheader = ""
        for i in range(3):
            stegheader += str(self.srcPixels[i, 0][0] & 1) + str(self.srcPixels[i, 0][1] & 1) + str(self.srcPixels[i, 0][2] & 1)
        a = int("0b" + stegheader[0:3], 2)
        b = int("0b" + stegheader[3:9], 2)

        iter = 0
        if stegheader != "001000000":
            indexgenerator = self.lcg(a, b, self.pixelCount, 3)
        else:
            indexgenerator = self.lcg(a, b, None, 3)

        for i in indexgenerator:
            if iter > self.pixelCount - 3 - 1:
                break
            x = i %  self.srcImage.size[0]
            y = i // self.srcImage.size[0]
            resultbin += str(self.srcPixels[x, y][0] & 0x1)
            resultbin += str(self.srcPixels[x, y][1] & 0x1)
            resultbin += str(self.srcPixels[x, y][2] & 0x1)
            iter += 1

        resultpayload = []
        for i in range(0, len(resultbin), 8):
            binstr = resultbin[i:i+8]
            if len(binstr) < 8:
                binstr = binstr.ljust(8, "0")

            binstr = "0b" + binstr
            resultpayload.append(int(binstr, 2))

        with open(self.outputName, "wb") as file:
            file.write(bytearray(resultpayload))



class StegWAV(Steg):
    def __init__(self, input : "str/fp", output : str):
        self.srcAudio   = wave.open(input, mode="rb")
        self.frameBytes = bytearray(list(self.srcAudio.readframes(self.srcAudio.getnframes())))
        self.outputName = output

    def encode(self, payload : str, key : str = None) -> bool:
        stegpayload = self.payloadToStegBinary(payload)
        if key is None:
            indexgenerator = self.lcg(1, 0, None, 8)
            stegheader    = "01000000"
        else:
            # 2 bit for a, 6 bit for b
            a = ord(key[0]) % 4
            b = sum([ord(c) for c in key]) % 64
            if b == 0:
                b = 1
            indexgenerator = self.lcg(a, b, len(self.frameBytes), 8)
            stegheader     = bin(a)[2:].zfill(2) + bin(b)[2:].zfill(6)

        # Header insertion
        for i in range(len(self.frameBytes)):
            if i < 8:
                self.frameBytes[i] = (self.frameBytes[i] & 0xFE) | int(stegheader[i])
            else:
                self.frameBytes[i] = self.frameBytes[i] & 0xFE

        # Payload insertion
        wav_idx = next(indexgenerator)
        for i in range(len(stegpayload)):
            self.frameBytes[wav_idx] |= int(stegpayload[i])
            wav_idx = next(indexgenerator)

        # Output
        resultpayload = bytes(self.frameBytes)
        with wave.open(self.outputName, "wb") as file:
            file.setparams(self.srcAudio.getparams())
            file.writeframes(resultpayload)
        return True

    def decode(self):
        stegheader = "".join([str(self.frameBytes[i] & 1) for i in range(8)])
        a = int("0b" + stegheader[0:2], 2)
        b = int("0b" + stegheader[2:8], 2)

        resultbin = ""
        iter = 0
        if stegheader != "01000000":
            indexgenerator = self.lcg(a, b, len(self.frameBytes), 8)
        else:
            indexgenerator = self.lcg(a, b, None, 8)

        for i in indexgenerator:
            if iter > len(self.frameBytes) - 8:
                break
            resultbin += str(self.frameBytes[i] & 0x1)
            iter += 1

        resultpayload = []
        for i in range(0, len(resultbin), 8):
            binstr = resultbin[i:i+8]
            if len(binstr) < 8:
                binstr = binstr.ljust(8, "0")

            binstr = "0b" + binstr
            resultpayload.append(int(binstr, 2))

        with open(self.outputName, "wb") as file:
            file.write(bytearray(resultpayload))


def psnr(cover : str, stego : str) -> float:
    buf1 = np.asarray(PIL.Image.open(cover))
    buf2 = np.asarray(PIL.Image.open(stego))
    rms  = np.mean((buf1-buf2)**2)
    return 20 * log(255/rms, 10)


def audiopsnr(cover : str, stego : str) -> float:
    wav1 = wave.open(cover, mode="rb")
    buf1 = np.array(list(wav1.readframes(wav1.getnframes())))
    wav2 = wave.open(stego, mode="rb")
    buf2 = np.array(list(wav2.readframes(wav2.getnframes())))
    rms  = np.mean((buf1-buf2)**2)
    return 20 * log(255/rms, 10)


# r = StegWAV("other/grav.wav", "hoho.wav")
# r.encode("haehaehae")
#
# w = StegWAV("hoho.wav", "q.txt")
# w.decode()

# q = StegPNG("../other/eve.png", "hehe.png")
# q.encode("hehe")
#
# #
# p = StegPNG("hehe.png", "uwu.txt")
# p.decode()
