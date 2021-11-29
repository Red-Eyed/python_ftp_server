#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Vadym Stupakov"
__email__ = "vadim.stupakov@gmail.com"

from subprocess import call
import sys
from shlex import split
import os
from pathlib import Path

ROOT_PATH = Path(__file__).parent
BUILD_DIR = ROOT_PATH / "build"
SCRIPT_PATH = ROOT_PATH / "python_ftp_server/ftp_server.py"

if __name__ == '__main__':
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    env["PYTHONUTF8"] = "1"
    env["PYTHONWARNINGS"] = "ignore"
    env["PYTHONNOUSERSITE"] = "1"

    opts = split(f"""
                 --clean
                 --noupx
                 --onefile
                 --noconfirm
                 --workpath={BUILD_DIR.as_posix()}/work_dir
                 --specpath={BUILD_DIR.as_posix()}/work_dir
                 --distpath={ROOT_PATH.as_posix()}
                 --name=ftp_server {SCRIPT_PATH.as_posix()}
                 """
                 )

    call([sys.executable, "-m", "PyInstaller.__main__"] + opts, env=os.environ.copy())
