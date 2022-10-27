"""
All start here
First install:
python3 -m pip install -U pygame --user

Start program from 1 directory above with:
python3 wall

Lint with (from 1 directory above):
pylint --extension-pkg-whitelist=pygame wall

Create UML diagram (assuming pip3 install py2puml and from parent directory):
py2puml wall/wall wall
"""
from services.application_service import start

if __name__ == "__main__":
    start()
