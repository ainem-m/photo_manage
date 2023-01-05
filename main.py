from datetime import datetime
import os
import subprocess
from typing import List, Tuple, Optional, Generator
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
    return datetime.fromtimestamp(path.stat().st_mtime)


def date_to_str(date: datetime) -> str:
    return f"{date.year}-{date.month:02d}-{date.day:02d}"


def main():
    ROOT_DIR: Path = Path(STR_ROOT_DIR)
    TARGET_DIR: Path = Path(STR_TARGET_DIR)
    assert ROOT_DIR.exists() and TARGET_DIR.exists()

    (TARGET_DIR / "qr").mkdir(exist_ok=True)

    # ---
    # ファイルリストの取得
    jpg_filelist: Generator[Path, None, None] = ROOT_DIR.glob("*.jp?g")
    if next(jpg_filelist, None) is None:
        # 画像ファイルが見つからなかったとき
        jpg_filelist = ROOT_DIR.glob("*.JPG")
        if next(jpg_filelist, None) is None:
            raise FileNotFoundError("no files found")

    # 日付順にソート
    sorted_filelist: List[Tuple[Path, datetime]] = sorted(
        ((path, get_date(path)) for path in jpg_filelist), key=lambda x: x[1])

    current_time = sorted_filelist[0][1]
    target_dir: str = TARGET_DIR
    current_day: datetime.day = current_time.day
    file_number: int = 0

    for i, (path, date) in enumerate(sorted_filelist):
        folder_name: Optional[str] = decode.decode(path)
        # QRCodeが見つかったらフォルダを作成
        if folder_name or i == 0 or date.day != current_day:
            current_day = date.day
            if folder_name:
                target_dir = TARGET_DIR / folder_name
                # QRCodeの画像は避難
                qr_path: Path = TARGET_DIR / "qr" / \
                    f"{date_to_str(date)}-{file_number:02d}.jpg"
                while qr_path.exists():
                    print(
                        f"you may run this program twice: \n{qr_path} is already exists", file=sys.stderr)
                    file_number += 1
                    qr_path = qr_path.parent / \
                        f"{date_to_str(date)}-{file_number:02d}.jpg"

                shutil.copy(src=path, dst=qr_path)
                file_number += 1
                continue
            else:
                # QRCodeが見つからずに日付が変わった場合
                # おそらくQRCodeの撮り忘れなので、日付の名前のフォルダを作成
                target_dir = TARGET_DIR / (date_to_str(date) + "unknown")

        target_dir.mkdir(exist_ok=True)

        img_path: Path = target_dir / \
            f"{date_to_str(date)}-{file_number:02d}.jpg"

        while img_path.exists():
            print(
                f"you may run this program twice:\n{img_path} is already exists", file=sys.stderr)
            file_number += 1
            img_path = img_path.parent / \
                f"{date_to_str(date)}-{file_number:02d}.jpg"
        shutil.copy(src=path, dst=img_path)
        file_number += 1
    os.chdir(TARGET_DIR)
    res = subprocess.run("tree", capture_output=True, text=True)
    print(res.stdout, file=sys.stderr)


if __name__ == "__main__":
    main()
