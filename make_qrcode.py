import qrcode
import sys

# 使い方
# python3 make_qrcode.py text >hoge.jpg
# 引数に作りたい文字列を入力し、出力をリダイレクトして画像を保存
text = sys.argv[1]
img = qrcode.make(text)

img.save(sys.stdout)
