import datetime
import os
import subprocess
import cv2
from typing import List, Tuple, Optional
import glob
import shutil
import sys

# ---
# 設定

# 振り分ける対象のフォルダ
ROOT_DIR: str = "/Users/ainem/Desktop/python/photo_manage/sample/"
# 振り分け先のフォルダ
TARGET_DIR: str = "/Users/ainem/Desktop/python/photo_manage/sample2/"

# ---


def get_date(path: str) -> datetime.datetime:
    update_time = os.path.getatime(path)
    return datetime.datetime.fromtimestamp(update_time)


def decode(path: str) -> Optional[str]:
    img = cv2.imread(path)
    qcd = cv2.QRCodeDetector()
    retval, _, _ = qcd.detectAndDecode(img)
    if retval:
        return retval
    return None


def date_to_str(date: datetime.datetime) -> str:
    return f"{date.year}-{date.month:02d}-{date.day:02d}"


def main():
    try:
        os.mkdir(TARGET_DIR + "qr")
    except FileExistsError:
        pass

    # ---
    # ファイルリストの取得
    os.chdir(ROOT_DIR)
    jpg_filelist: List[str] = glob.glob("*.jp?g")
    if not jpg_filelist:
        raise FileNotFoundError("no files found")

    # 日付順にソート
    sorted_filelist: List[Tuple[str, datetime.datetime]] = sorted(
        ((path, get_date(path)) for path in jpg_filelist), key=lambda x: x[1])

    current_time = sorted_filelist[0][1]
    target_dir: str = TARGET_DIR
    current_day: datetime.datetime.day = current_time.day
    cnt: int = 0

    for i, (path, date) in enumerate(sorted_filelist):
        folder_name = decode(path)
        # QRCodeが見つかったらフォルダを作成
        if folder_name or i == 0 or date.day != current_day:
            current_day = date.day
            target_dir = TARGET_DIR
            if not folder_name or not folder_name.isdigit():
                # QRCodeが見つからずに日付が変わった場合
                # おそらくQRCodeの撮り忘れなので、日付の名前のフォルダを作成
                # QRCodeの読み込み結果が数字ではない場合も同様
                target_dir = TARGET_DIR + date_to_str(date)
            try:
                os.mkdir(target_dir)
            except FileExistsError:
                # 既に同名のフォルダが存在していたら何もしない
                pass
            if folder_name:
                # QRCodeの画像は避難
                qr_path: str = f"{TARGET_DIR}qr/{date_to_str(date)}-{cnt:02d}.jpg"
                while os.path.isfile(qr_path):
                    print(
                        f"you may run this program twice: \n{qr_path} is already exists", file=sys.stderr)
                    cnt += 1
                    qr_path = f"{TARGET_DIR}qr/{date_to_str(date)}-{cnt:02d}.jpg"
                shutil.copy(src=path, dst=qr_path)
                cnt += 1
                continue

        img_path: str = f"{target_dir}/{date_to_str(date)}-{cnt:02d}.jpg"
        while os.path.isfile(img_path):
            print(
                f"you may run this program twice:\n{img_path} is already exists", file=sys.stderr)
            cnt += 1
            img_path = f"{target_dir}/{date_to_str(date)}-{cnt:02d}.jpg"
        shutil.copy(src=path, dst=img_path)
        cnt += 1
    os.chdir(TARGET_DIR)
    res = subprocess.run("tree", capture_output=True, text=True)
    print(res.stdout, file=sys.stderr)


if __name__ == "__main__":
    main()
