from setuptools import setup
import re
import os
import platform

with open('{}/README.md'.format(os.path.split(os.path.abspath(__file__))[0]), 'r') as inf:
    long_description = inf.read()

with open('{}/src/r2g_gui/__init__.py'.format(os.path.split(os.path.abspath(__file__))[0]), 'r') as inf:
    version = re.findall(r'__version__ = "(.+)"', inf.read())[0]

# A known bug in docker-py:
# 1. https://github.com/docker/docker-py/issues/1870
# 2. https://github.com/mhammond/pywin32/issues/1431
# 3. https://github.com/twosixlabs/armory/issues/156
# It can be fixed by "conda install pywin32"
requirements = ["PyQt5>=5.12", "docker[tls]~=4.3.1"]
if platform.system() == "Windows":
    requirements.append("pywin32>=227")

setup(
    name='r2g_gui',
    version=version,
    license="MIT",
    url='https://github.com/yangwu91/r2g_gui.git',
    author='Yang Wu',
    author_email='wuyang@drwu.ga',
    maintainer="Yang Wu",
    maintainer_email="wuyang@drwu.ga",
    description='A GUI for r2g, which is a homology-based, computationally lightweight pipeline for '
                'discovering genes in the absence of an assembly',
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires='>=3.6',
    scripts=['src/scripts/r2g.gui.py'],
    # py_modules=['r2g_gui.errors', ],
    packages=[
        "r2g_gui",
        "r2g_gui.main",
        "r2g_gui.dialogs",
    ],
    package_dir={"": "src"},
    package_data={'r2g_gui': ['fonts/*.ttf', 'images/*']},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering :: Bio-Informatics"
    ],
    install_requires=requirements,
    extras_require={
        'cli': ["r2g>=1.0.5", "requests~=2.24.0", "selenium~=3.141.0"],
        'test': ["pytest", "pytest-cov", "codecov"],
    },
)
