from setuptools import find_packages, setup

setup(
    name='konfio_extractors',
    version='0.1',
    description='Konfio extractor package',
    author='Javier Amaya Patricio',
    packages=find_packages(),
    install_requires=[
        'requests==2.32.3',
    ],
    python_requires='>=3.8',
    package_dir={'': '.'},
)
