# Easy Cross-platform Building for BDWGC

This project provides a simple way to build the Boehm-Demers-Weiser conservative C/C++ Garbage Collector ([bdwgc](https://github.com/ivmai/bdwgc)).

# Prerequisites

1. Clone required git repositories:
   1. `git clone https://github.com/ivmai/bdwgc -b v8.2.4`
   2. `git clone https://github.com/ivmai/libatomic_ops bdwgc/libatomic_ops -b v7.8.0`

2. Zig: Install the [`zig`](https://author.ciweimao.com/#navid-homepage) compiler. For Windows users, `scoop install zig` is recommended, which uses the [Scoop](https://scoop.sh/) package manager.

3. Python Pmakefile: `pip install pmakefile` with Python 3.8+.

## Build

```bash
python make.py build-win-x64     # output dist/x86_64/libgc.dll
python make.py build-linux-x64   # output dist/x86_64/libgc.so

# need a macos machine to include <CoreFoundation.h>, etc.
python make.py build-macos-x64   # output dist/x86_64/libgc.dylib
```
