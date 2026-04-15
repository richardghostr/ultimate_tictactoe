"""Build a wheel for the project and place it in `dist/`.

Usage:
    python scripts/build_wheel.py
"""
import subprocess
import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

def build():
    cmd = [sys.executable, '-m', 'build']
    print('Running:', ' '.join(cmd))
    subprocess.check_call(cmd)

if __name__ == '__main__':
    build()
