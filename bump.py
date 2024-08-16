import os
import sys
import re

def read_version():
    with open('upsonic/__init__.py', 'r') as file:
        for line in file:
            match = re.search(r"__version__ = '(.*)'", line) # fmt: skip
            if match:
                return match.group(1)

def increment_version(part, version):
    major, minor, patch = map(int, version.split('.'))
    if part == 'major':
        major += 1
        minor = 0
        patch = 0
    elif part == 'minor':
        minor += 1
        patch = 0
    elif part == 'patch':
        patch += 1
    return f'{major}.{minor}.{patch}'

def write_version(version):
    with open('upsonic/__init__.py', 'r+') as file:
        content = file.read()
        content = re.sub(r"__version__ = '.*'", f"__version__ = '{version}'", content) # fmt: skip
        file.seek(0)
        file.write(content)

def update_version(version):
    files = ['setup.py']
    for file in files:
        with open(file, 'r+') as f:
            content = f.read()
            content = re.sub(r'    version=".*"', f'    version="{version}"', content) # fmt: skip
            f.seek(0)
            f.write(content)

def create_tag(version):
    os.system(f"git tag v{version}")

def create_commit(version):
    os.system("git add .")
    os.system(f"git commit -m 'Changed version number with v{version}'")


def push():
    os.system("git push")
    os.system("git push --tag")

def main():
    part = sys.argv[1]
    version = read_version()
    new_version = increment_version(part, version)
    write_version(new_version)
    update_version(new_version)
    create_commit(new_version)
    create_tag(new_version)
    push()

if __name__ == '__main__':
    main()

