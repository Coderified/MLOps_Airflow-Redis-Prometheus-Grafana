#For project managmt

from setuptools import setup, find_packages


with open("requirements.txt") as f:
    requirements = f.read().splitlines()


setup(
    name = 'MLOPS Proj3ect',
    version = "0.1",
    author = "Bharath",
    packages = find_packages(),
    install_requires = requirements,
)