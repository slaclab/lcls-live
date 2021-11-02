"""Setup module for lcls_live"""
import versioneer


from setuptools import setup, find_packages
from os import path, environ

cur_dir = path.abspath(path.dirname(__file__))

with open(path.join(cur_dir, 'requirements.txt'), 'r') as f:
    requirements = f.read().split()



setup(
    name='lcls-live',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages(),  
    package_dir={'lcls_live':'lcls_live'},
    author='Christopher Mayes',
    author_email='cmayes@slac.stanford.edu',
    
    url='https://github.com/slaclab/lcls-live',
    keywords='model lcls tao',
    description='Tools for interacting with Tao using live data from LCLS.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=requirements,
    include_package_data=True,
    python_requires='>=3.6',
    entry_points={
    'console_scripts': [
        'get-lcls-live=lcls_live.command_line:main'],
    },
    scripts = ["scripts/configure-epics-remote", "scripts/configure-archiver-remote"]
)
