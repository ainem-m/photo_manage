import qrcode
import sys

# 使い方
# python3 make_qrcode.py >hoge.jpg
# のようにして出力をリダイレクトして使う
# TODO: シェルで引数を取れるようにしたい
text = input("text: ")
img = qrcode.make(text)

img.save(sys.stdout)
