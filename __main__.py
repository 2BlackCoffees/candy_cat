"""

Lint with (from 1 directory above):
pylint --extension-pkg-whitelist=pygame wall

Create UML diagram (assuming pip3 install py2puml and from parent directory):
py2puml wall/wall wall
"""
from services.application_service import start

if __name__ == "__main__":
    start()
