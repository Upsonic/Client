import os
import re
import sys

def write_version(version):
    with open("upsonic/__init__.py", "r+") as file:
        content = file.read()
        content = re.sub(r"__version__ = '.*'", f"__version__ = '{version}'", content)  # fmt: skip
        file.seek(0)
        file.write(content)

def update_version_in_setup(version):
    with open("setup.py", "r+") as file:
        content = file.read()
        content = re.sub(r'    version=".*"', f'    version="{version}"', content)  # fmt: skip
        file.seek(0)
        file.write(content)

def create_tag(version):
    os.system(f"git tag v{version}")

def create_commit(version):
    os.system("git add .")
    os.system(f"git commit -m 'Changed version number to v{version}'")

def push():
    os.system("git push")
    os.system("git push --tags")

def main():
    if len(sys.argv) != 2:
        print("Usage: python sync.py <new_version>")
        sys.exit(1)

    new_version = sys.argv[1]
    write_version(new_version)
    update_version_in_setup(new_version)
    create_commit(new_version)
    create_tag(new_version)
    push()

if __name__ == "__main__":
    main()