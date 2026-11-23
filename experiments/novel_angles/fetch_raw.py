"""Populate git-annex objects in an OpenNeuro ds007176 v1.0.1 checkout."""
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from pathlib import Path
import argparse
import os
import re
import subprocess
from time import sleep
from urllib.parse import quote
from urllib.request import urlopen


REVISION = "1ef1c74a5c0b5ac84a098afecfe1d53b9cc8aa0f"
VISITS = ("V0", "V1", "V2")
TASKS = ("CE", "OE")


def inventory(root):
    paths = list(root.glob("sub-*/ses-*/eeg/*_eeg.vhdr"))
    recordings = {}
    for path in paths:
        match = re.fullmatch(r"(sub-[^_]+)_ses-(V\d+)_task-(CE|OE)_eeg", path.stem)
        if match:
            subject, visit, task = match.groups()
            recordings.setdefault(subject, {}).setdefault(visit, {})[task] = path
    complete = {}
    for subject, visits in sorted(recordings.items()):
        paired = {v: tasks for v, tasks in visits.items() if set(tasks) == set(TASKS)}
        later = sorted(set(paired) & {"V3", "V4"})
        if set(VISITS) <= paired.keys() and len(later) == 1:
            complete[subject] = {v: paired[v] for v in (*VISITS, later[0])}
    return complete


def fetch(root, path):
    if not path.is_symlink():
        raise ValueError(f"Expected an annex pointer: {path}")
    target = path.resolve()
    match = re.fullmatch(r"SHA256E-s(\d+)--([a-f0-9]{64})\..+", target.name)
    if not match:
        raise ValueError(f"Expected a SHA256E annex pointer: {path}")
    size, digest = match.groups()
    if target.exists() and target.stat().st_size == int(size):
        return
    url = "https://s3.amazonaws.com/openneuro.org/ds007176/" + quote(str(path.relative_to(root)))
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(".partial")
    for attempt in range(3):
        try:
            checksum = sha256()
            with urlopen(url, timeout=90) as response, temporary.open("wb") as output:
                while block := response.read(1024 * 1024):
                    output.write(block)
                    checksum.update(block)
            if checksum.hexdigest() != digest or temporary.stat().st_size != int(size):
                raise ValueError(f"S3 object does not match the pinned snapshot: {path}")
            os.replace(temporary, target)
            return
        except OSError:
            if attempt == 2:
                raise
            sleep(attempt + 1)
        finally:
            temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--workers", type=int, default=12)
    args = parser.parse_args()
    root = args.root.resolve()
    head = subprocess.check_output(["git", "-C", root, "rev-parse", "HEAD"], text=True).strip()
    if head != REVISION:
        parser.error(f"Expected ds007176 v1.0.1 ({REVISION}); got {head}")
    subjects = inventory(root)
    if len(subjects) != 29:
        parser.error(f"Expected 29 complete subjects; got {len(subjects)}")
    paths = [path.with_suffix(ext) for visits in subjects.values() for tasks in visits.values()
             for path in tasks.values() for ext in (".eeg", ".vhdr", ".vmrk")]
    with ThreadPoolExecutor(args.workers) as pool:
        for done, _ in enumerate(pool.map(lambda path: fetch(root, path), paths), start=1):
            if done % 60 == 0 or done == len(paths):
                print(f"Snapshot files present: {done}/{len(paths)}", flush=True)


if __name__ == "__main__":
    main()
