import os
from setuptools import setup, find_packages
from pathlib import Path


with open('requirements.txt', encoding="utf-8") as f:
    required = f.read().splitlines()
    install_requires = [item.strip() for item in required if item.strip()[0] != '#']

packages = find_packages(where='.')
# package_dir = {name: f"src/{name}" for name in packages}

setup(
    version="0.1",
    name='code_assistant',
    packages=packages,
    description='A simple assitant to improve code comment quality',
    install_requires=install_requires,
    include_package_data=True,
    entry_points={
            'console_scripts': [
                'comment_analyzer = code_assistant.main:main'
            ]
        },
)