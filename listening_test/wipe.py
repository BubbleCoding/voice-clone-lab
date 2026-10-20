"""Delete all listening-test audio and the database: python -m listening_test.wipe [--yes]"""

import argparse
import shutil

from .app import default_base_dir


def wipe(base_dir):
    shutil.rmtree(base_dir, ignore_errors=True)
    return not base_dir.exists()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--yes", action="store_true", help="skip the confirmation prompt")
    args = parser.parse_args()
    base_dir = default_base_dir()
    if not base_dir.exists():
        print(f"Nothing to wipe: {base_dir} does not exist.")
        return
    clips = list((base_dir / "uploads").glob("*.wav"))
    print(f"This deletes {len(clips)} uploaded clips, all ratings and the pair codes in {base_dir}.")
    if not args.yes and input("Continue? [y/N] ").strip().lower() != "y":
        print("Cancelled.")
        return
    print("Wiped." if wipe(base_dir) else f"Could not delete {base_dir}.")


if __name__ == "__main__":
    main()
