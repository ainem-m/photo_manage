import qrcode
import sys
text = input()
img = qrcode.make(text)

img.save(sys.stdout)
