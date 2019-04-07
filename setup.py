from setuptools import setup, find_packages

for line in open('dosa/__init__.py'):
    if line.startswith('__version__'):
        version = line.split('=')[-1].strip()[1:-1]
        break

setup(
    name='dosa',
    version=version,
    url='https://github.com/shon/dosa/',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3'
        ],
    include_package_data=True,
    description='Python wrapper for Digital Ocean API V2',
    long_description=open('README.rst').read(),
    packages=find_packages(),
    author='Shekhar Tiwatne',
    author_email='pythonic@gmail.com',
    license="http://www.opensource.org/licenses/mit-license.php",
    test_suite="tests",
    install_requires=['requests']
    )
