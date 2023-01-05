from datetime import datetime
import subprocess
from typing import List, Tuple, Optional
import shutil
import sys
from pathlib import Path
import decode
import settings


def get_date(path: Path) -> datetime:
    return datetime.fromtimestamp(path.stat().st_mtime)


def date_to_str(date: datetime) -> str:
    return f"{date.year}-{date.month:02d}-{date.day:02d}"


def make_filepath(dst: Path, date: datetime, cnt: int) -> Tuple[Path, int]:
    path = dst / f"{date_to_str(date)}-{cnt:02d}.jpg"
    if path.exists():
        print("you may run this program twice:", file=sys.stderr)
        print(f"{path} is already exists", file=sys.stderr)
        while path.exists():
            cnt += 1
            path = path.parent / f"{date_to_str(date)}-{cnt:02d}.jpg"
    return path, cnt


def main():
    ROOT_DIR: Path = Path(settings.ROOT_DIR)
    TARGET_DIR: Path = Path(settings.TARGET_DIR)
    assert ROOT_DIR.exists() and TARGET_DIR.exists()

    (TARGET_DIR / "qr").mkdir(exist_ok=True)

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
        if folder_name:
            current_day = date.day
            # QRCodeが見つかったらフォルダを作成
            target_dir = TARGET_DIR / folder_name
            target_dir.mkdir(exist_ok=True)
            # QRCodeの画像は避難
            qr_path, cnt = make_filepath(TARGET_DIR / "qr", date, cnt)
            shutil.copy(src=path, dst=qr_path)
            cnt += 1
            continue
        if i == 0 or date.day != current_day:
            current_day = date.day
            # QRCodeが見つからずに日付が変わった場合
            # おそらくQRCodeの撮り忘れなので、日付の名前のフォルダを作成
            target_dir = TARGET_DIR / (date_to_str(date) + "unknown")

        target_dir.mkdir(exist_ok=True)

        img_path, cnt = make_filepath(target_dir, date, cnt)
        shutil.copy(src=path, dst=img_path)
        cnt += 1
    subprocess.run(f"chdir {TARGET_DIR}")
    res = subprocess.run("tree", capture_output=True, text=True)
    print(res.stdout, file=sys.stderr)


if __name__ == "__main__":
    main()
