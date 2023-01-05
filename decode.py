import cv2
from typing import Optional
import pathlib


def resize(img: cv2.Mat, size: int = 1024, debug: bool = False) -> cv2.Mat:
    h, w = img.shape[:2]
    if debug:
        print("before: ", h, w)
    if w > h:
        ratio: float = size/w
        w = size
        h = int(h*ratio)
    else:
        ratio: float = size/h
        w = int(w*ratio)
        h = size
    if debug:
        print("resize: ", h, w)
    return cv2.resize(img, dsize=(w, h))


def decode(path: pathlib.Path, debug=False) -> Optional[str]:
    img = cv2.imread(str(path))
    # 画像サイズが大きいと読み取りがうまく行かないので
    # アスペクト比を保ったまま長辺が1024になるように縮小
    img = resize(img, debug=debug)
    if debug:
        cv2.imshow("", img)
        cv2.waitKey()
    qcd = cv2.QRCodeDetector()
    retval, _, _ = qcd.detectAndDecode(img)
    if retval:
        return retval
    else:
        img = resize(img, 512, debug=debug)
        retval, _, _ = qcd.detectAndDecode(img)
        return retval


if __name__ == "__main__":
    path = pathlib.Path(input())
    print(decode(path, debug=True))
