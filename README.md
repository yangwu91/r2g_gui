# Reads to Genes (r2g) GUI 

![PyPI](https://img.shields.io/pypi/v/r2g_gui?logo=pypi&style=plastic) ![py_ver](https://img.shields.io/pypi/pyversions/r2g_gui?logo=python&style=plastic) ![licence](https://img.shields.io/github/license/yangwu91/r2g_gui?logo=open-source-initiative&style=plastic)


## Introduction

<div align=center><img src="https://raw.githubusercontent.com/yangwu91/r2g_gui/main/images/screenshot.png" alt="screenshot"/></div>

This is the GUI wrapper for **Reads to Genes**, or **r2g**, which is a homology-based, computationally lightweight pipeline for discovering genes in the absence of an assembly. The r2g core is hosted on https://github.com/yangwu91/r2g.

The `r2g GUI` is still under developing, please feel free to file an issue or [email me](mailto:wuyang@drwu.ga?subject=R2g%20GUI%20issues).

## Implementation

### Install Docker

Please follow the instruction [here](https://docs.docker.com/get-docker/) to download and install Docker based on your operating system before running the `r2g GUI`. The Docker software is compatible with most common operating systems including Linux, macOS and Windows.

### Install `r2g GUI`

You can choose one of the following methods to install the `r2g GUI`:

* Download zipped pre-built binary files (**Python 3 environment is NOT required**)

  | Operating System | Size (Mb) | MD5                              | Download link                 |
  | ---------------- | --------- | -------------------------------- | ----------------------------- |
  | Windows          | 40.58     | 6ce77067905cb0d7e5c17934a018da76 | [r2g_gui-0.1.0-Windows.zip](https://github.com/yangwu91/r2g_gui/releases/download/v0.1.0/r2g_gui-0.1.0-Windows.zip) |
  | macOS            | 30.10     | f719b82ba47e74b758a2505aecb4c5ad | [r2g_gui-0.1.0-macOS.zip](https://github.com/yangwu91/r2g_gui/releases/download/v0.1.0/r2g_gui-0.1.0-macOS.zip)   |

  ⚠️ Please note that Windows Defender will report it as `Trojan:Win32/Wacatac.B!ml`, which is **false positive**. Add the `r2g.exe` to the excluding list of Windows Defender for further use. Please check out the scanning results on [https://virustotal.com](https://www.virustotal.com/gui/file/c6a235bd3ef7497de19a8e0fbf251ba9526e6321110a32b891e419a7ff0a6e34/detection).  Or maybe you can try the other method if the Python 3 environment has been installed on your computer.

  <div align=center><img src="https://raw.githubusercontent.com/yangwu91/r2g_gui/main/images/windows_defender.png" alt="windows_defender"/></div>

* Install by PyPI (**Python 3 environment is required**)

  If Python 3 and the `pip` utility has been installed on your computer, the `r2g GUI` can be installed by the command as follows:

  `pip install r2g_gui`

## Usage

1. Please run the Docker (i.e. Docker Desktop on WIndows/macOS or Docker Deamon on Linux) before start the r2g job. 

2. Start the `r2g GUI`. At the first time, the r2g GUI will pull the latest image of the r2g Docker, which should take a while depending on your network quality. 

   * Windows

     Unzip the `r2g_gui-*.*.*-Windows.zip`, and then double click `r2g.exe`. 

     <div align=center><img src="https://raw.githubusercontent.com/yangwu91/r2g_gui/main/images/win.png" alt="win"/></div>

   * macOS

     Unzip the `r2g_gui-*.*.*-macOS.zip`. Hold `Control` and click `r2g.app`, or right click `r2g.app`, then click `open`.

     <div align=center><img src="https://raw.githubusercontent.com/yangwu91/r2g_gui/main/images/mac.png" alt="mac"/></div>

   * Other systems with Python 3 environment (installed by PyPI)

     Simply typing `r2g.gui.py` in the terminal should call the `r2g GUI`.

3. Fill in the parameters and hit the `Start!` button to submit the job. In addition, here is an example configuration. To use it, please click `File` -> `Import parameters...` and then select it, the GUI wrapper will load pre-configured parameters automatically. Hit the `Start!` button and enjoy!

## Tweak parameters

The `r2g GUI` is the GUI wrapper for the `r2g`, please check out [the detailed usage](https://github.com/yangwu91/r2g#usage) of `r2g` to tweak parameters.