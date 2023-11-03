from setuptools import find_packages, setup

setup(
    name="barash",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "Click",
    ],
    entry_points={
        "console_scripts": [
            "barash = cli:cli",
        ],
    },
)
