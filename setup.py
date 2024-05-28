# setup.py
from setuptools import setup, find_packages

setup(
    name='PanKEGG',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Flask',
        'pandas',
        'numpy',
        'scikit-learn',
        'scipy'
    ],
    author='Vanbelle Arnaud',
    author_email='arnaudvanbelle@live.be.com',
    description='Application PanKEGG',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Avanbelle/PanKEGG.git',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)