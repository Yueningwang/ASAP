from setuptools import setup, find_packages

setup(
    name='Solar_Calculation',
    version='0.1dev0',
    packages=find_packages(exclude=['tests']),
    license='MIT',
    long_description=open('README.md').read(),
    url='https://github.com/Yueningwang/ASAP',
)
