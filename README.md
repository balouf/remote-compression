# Remote Compression


[![PyPI Status](https://img.shields.io/pypi/v/remote-compression.svg)](https://pypi.python.org/pypi/remote-compression)
[![Build Status](https://github.com/balouf/remote-compression/actions/workflows/build.yml/badge.svg?branch=main)](https://github.com/balouf/remote-compression/actions?query=workflow%3Abuild)
[![Documentation Status](https://github.com/balouf/remote-compression/actions/workflows/docs.yml/badge.svg?branch=main)](https://github.com/balouf/remote-compression/actions?query=workflow%3Adocs)
[![License](https://img.shields.io/github/license/balouf/remote-compression)](https://github.com/balouf/remote-compression/blob/main/LICENSE)
[![Code Coverage](https://codecov.io/gh/balouf/remote-compression/branch/main/graphs/badge.svg)](https://codecov.io/gh/balouf/remote-compression/tree/main)

rcomp helps to perform x265 video compression on remote server.


- Free software: MIT license
- Documentation: https://balouf.github.io/remote-compression/.


## Requirements

- `ffprobe` must be in the path of the local machine
- `ffmpeg` must be in the path of the remote server
- `.ssh/config` must enable direct connection to remote server
  - private key
  - proxyjump if required

## Usage

`$ rcomp --help`

## Credits

This package was created with [Cookiecutter][CC] and the [Package Helper 3][PH3] project template.

[CC]: https://github.com/audreyr/cookiecutter
[PH3]: https://balouf.github.io/package-helper-3/
