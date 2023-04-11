from setuptools import setup, find_packages

with open('requirements.txt', 'r') as fp:
    requirements = fp.read().splitlines()

setup(
    name='coinhunt',
    version='0.0.1',
    description='A Bitcoin private key finder',
    packages=find_packages(),
    requires=requirements
)

