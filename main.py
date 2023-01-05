from datetime import datetime
import os
import subprocess
from typing import List, Tuple, Optional
import shutil
import sys
from pathlib import Path
import decode
# ---
# 設定

# 振り分ける対象のフォルダ
STR_ROOT_DIR: str = "/Users/ainem/Desktop/python/photo_manage/sample/"
# 振り分け先のフォルダ
STR_TARGET_DIR: str = "/Users/ainem/Desktop/python/photo_manage/sample2/"

# ---


def get_date(path: Path) -> datetime:
    return datetime.fromtimestamp(path.stat().st_atime)


def date_to_str(date: datetime) -> str:
    return f"{date.year}-{date.month:02d}-{date.day:02d}"


def main():
    ROOT_DIR: Path = Path(STR_ROOT_DIR)
    TARGET_DIR: Path = Path(STR_TARGET_DIR)

    try:
        os.mkdir(TARGET_DIR / "qr")
    except FileExistsError:
        pass

    # ---
    # ファイルリストの取得
    jpg_filelist: List[str] = ROOT_DIR.glob("*.jp?g")
    if not jpg_filelist:
        raise FileNotFoundError("no files found")

    # 日付順にソート
    sorted_filelist: List[Tuple[Path, datetime]] = sorted(
        ((path, get_date(path)) for path in jpg_filelist), key=lambda x: x[1])

    current_time = sorted_filelist[0][1]
    target_dir: str = TARGET_DIR
    current_day: datetime.day = current_time.day
    cnt: int = 0

    for i, (path, date) in enumerate(sorted_filelist):
        folder_name: Optional[str] = decode.decode(path)
        # QRCodeが見つかったらフォルダを作成
        if folder_name or i == 0 or date.day != current_day:
            current_day = date.day
            target_dir: Path = TARGET_DIR
            if not folder_name or not folder_name.isdigit():
                # QRCodeが見つからずに日付が変わった場合
                # おそらくQRCodeの撮り忘れなので、日付の名前のフォルダを作成
                # QRCodeの読み込み結果が数字ではない場合も同様
                target_dir = TARGET_DIR / date_to_str(date)
            else:
                target_dir /= folder_name
            try:
                os.mkdir(target_dir)
            except FileExistsError:
                # 既に同名のフォルダが存在していたら何もしない
                pass
            if folder_name:
                # QRCodeの画像は避難
                qr_path: Path = TARGET_DIR / "qr" / \
                    f"{date_to_str(date)}-{cnt:02d}.jpg"
                while qr_path.exists():
                    print(
                        f"you may run this program twice: \n{qr_path} is already exists", file=sys.stderr)
                    cnt += 1
                    qr_path = qr_path.parent / \
                        f"{date_to_str(date)}-{cnt:02d}.jpg"

                shutil.copy(src=path, dst=qr_path)
                cnt += 1
                continue

        img_path: Path = target_dir / f"{date_to_str(date)}-{cnt:02d}.jpg"

        while img_path.exists():
            print(
                f"you may run this program twice:\n{img_path} is already exists", file=sys.stderr)
            cnt += 1
            img_path = img_path.parent / f"{date_to_str(date)}-{cnt:02d}.jpg"
        shutil.copy(src=path, dst=img_path)
        cnt += 1
    os.chdir(TARGET_DIR)
    res = subprocess.run("tree", capture_output=True, text=True)
    print(res.stdout, file=sys.stderr)


if __name__ == "__main__":
    main()
