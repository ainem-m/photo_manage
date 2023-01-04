# 写真自動振り分けソフト


## 制作の動機
歯科では、治療の説明や、粘膜の様子の記録のために口腔内写真を撮影することが多い。
撮影した写真は院内のPCに保存するが、手作業であり、めんどくさい。

患者にはそれぞれ番号が割り振られているので、あらかじめ患者番号を埋め込んだQRCodeを印刷し、撮影を始める前にそれを撮影することで、自動的に振り分けるようにしたい。
ちなみに、既にそのような仕組みをもつソフトウェア([松風シュアファイル](https://www.shofu.co.jp/surefile/index.html))があるが、対応したカメラの購入が必要であり、その、つまり、私は対応したカメラを所持していないのである。

## 動作のイメージ
![](images/carte_and_qr.png)
患者番号を埋め込んだQRを用意
![](images/shoot_qr.png)
写真撮影の前にQRコードを撮影
![](images/shoot_oral.png)
写真撮影

撮影後、SDカードを写真保管用PCに挿入
```zsh
. // SDカードフォルダ
├── 0000.jpg // バーコードを写したもの
├── 0001.jpg
├── 0002.jpg
├── 0003.jpg // バーコードを写したもの
├── 0004.jpg
└── 0005.jpg
```
以上のファイル構成で、  
`0000.jpg`のバーコードの中身が`folder1`  
`0003.jpg`のバーコードの中身が`folder2`  
2023年1月3日に実行したとすると、  
ファイルが更新日時順に`YYYY-MM-DD-cnt.jpg`の形式へリネームされ、
```zsh
.
├── qr
│   ├── 2023-01-03-00.jpg
│   └── 2023-01-03-03.jpg
├── folder1
│   ├── 2023-01-03-01.jpg
│   └── 2023-01-03-02.jpg
└── folder2
    ├── 2023-01-03-04.jpg
    └── 2023-01-03-05.jpg
```
このようにファイルが振り分けられる。

> TODO: 振り分け先を工夫して患者情報管理システムとリンクさせる？
> 
## 実装
#### ファイルリストの取得
ちょっと冗長な気もするが、まずファイルリストを取得してから、それぞれのファイルの作成日時を取得してソートする

##### globでjpgファイルのリストを取得
[ディレクトリ内のファイルリストを取得する – Pythonプログラミング物語](https://pcl.solima.net/pyblog/archives/512)
```Python
# 振り分ける対象のフォルダ
ROOT_DIR: str = "/photo_manage/sample/"
# 振り分け先のフォルダ
TARGET_DIR: str = "/photo_manage/sample2/"
try:
    os.mkdir(TARGET_DIR + "qr")
except FileExistsError:
    pass

# ---
# ファイルリストの取得
os.chdir(ROOT_DIR)
jpg_filelist: List[str] = glob.glob("*.jpg")
if not jpg_filelist:
    raise FileNotFoundError("no files found")

```

##### ファイルから更新日時を取得し、ソート
[Pythonでファイルの作成・更新日時を取得する（os.path.getmtimeなど）：作成日時の取得はOSごとに変わるので注意 - MathPython](https://www.mathpython.com/file-date)
*振り分け先が同じなのに日付が違う場合、バーコードの撮り忘れの可能性があるので、日付順の管理にする*
```python
# 日付順にソート
sorted_filelist: List[Tuple[str, datetime.datetime]] = sorted(
    ((path, get_date(path)) for path in jpg_filelist), key=lambda x: x[1])
```

#### バーコードファイルかそうでないか
画像からQRコード認識
[Python, OpenCVでQRコードを検出・読み取り | note.nkmk.me](https://note.nkmk.me/python-opencv-qrcode/)
```python
import cv2
def decode(path: str) -> Optional[str]:
    img = cv2.imread(path)
    qcd = cv2.QRCodeDetector()
    # retval(読み込み結果)のみ必要で、他の返り値は使わないため_で受け取る
    retval, _, _ = qcd.detectAndDecode(img)
    if retval:
        return retval
    return None
```

#### フォルダ作成
[Pythonでディレクトリ（フォルダ）を作成するmkdir, makedirs | note.nkmk.me](https://note.nkmk.me/python-os-mkdir-makedirs/)
`subprocess.run()`で行うより、`os.mkdir()`の方がエラーハンドリングしやすそう
```python
try:
    os.mkdir(target_dir)
except FileExistsError:
    # 既に同名のフォルダが存在していたら何もしない
    pass
```


#### ファイルの移動
[Pythonでファイル・ディレクトリを移動するshutil.move | note.nkmk.me](https://note.nkmk.me/python-shutil-move/)

#### コメントの追加？
プロンプトを表示し、もしフォルダに情報を追加したい場合は追加？
逆にめんどくさいか？

#### treeの結果を表示
標準エラー出力に、移動先フォルダの`tree`の結果を表示する。でも結構大きな出力になるからいらないかも。