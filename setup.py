from setuptools import setup, find_packages

setup(
    name='Solar_Calculation',
    version='0.1dev1',
    description='Identify potential solar sites and compute potential solar energy',
    long_description=open('README.md').read(),
    url='https://github.com/Yueningwang/ASAP',
    author='Jingtian Zhang, Cheng Zeng, Yuening Wang',
    author_email='zengcheng95@gmail.com',
    license='MIT',
    keywords='solar energy',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'python_version == 2.7',
    ],
    project_urls={
        'Bug Reports': 'https://github.com/Yueningwang/ASAP/issues',
        'Source': 'https://github.com/Yueningwang/ASAP',
    },
)
