import os
import subprocess


def open_file(path: str) -> None:
    os.startfile(path)


def reveal_in_explorer(path: str) -> None:
    subprocess.Popen(f"explorer /select,{path}")
