from __future__ import annotations
from pmakefile import *  # type: ignore
from dataclasses import dataclass
from contextlib import contextmanager
import os
import subprocess
import typing

phony(
    [
        "build-win-x64",
        "build-macos-x64",
        "build-linux-x64",
    ]
)

CC = ["zig", "cc"]

BDWGC_DEFAULT_FLAGS = [
    # "-DALL_INTERIOR_POINTERS",
    "-DENABLE_DISCLAIM",
    "-DGC_ATOMIC_UNCOLLECTABLE",
    "-DGC_GCJ_SUPPORT",
    "-DJAVA_FINALIZATION",
    "-DNO_EXECUTE_PERMISSION",
    "-DUSE_MMAP",
    "-DUSE_MUNMAP",
]

CFLAGS = [
    "-DGC_THREADS",
    "-DPARALLEL_MARK",
    "-DTHREAD_LOCAL_ALLOC",
    *BDWGC_DEFAULT_FLAGS,
]
CFLAGS.append("-fPIC")
CFLAGS.append("-O2")

IncludeDirs = ["./bdwgc/include", "./bdwgc/libatomic_ops/src"]

SourceFiles = [file for file in os.listdir("./bdwgc") if file.endswith(".c")]
SourceFiles = [os.path.join("./bdwgc", file) for file in SourceFiles]

ROOT = Path(__file__).parent


@dataclass
class BuildTarget:
    arch: typing.Literal["x86_64", "aarch64"]
    os: typing.Literal["linux", "macos", "windows"]

    def compute_zig_target(self) -> str:
        if self.os == "linux":
            return f"{self.arch}-linux-gnu"
        elif self.os == "macos":
            return f"{self.arch}-macos-none"
        elif self.os == "windows":
            return f"{self.arch}-windows-gnu"
        else:
            raise Exception(f"Unknown OS: {self.os}")

    def get_dl_ext(self) -> str:
        if self.os == "linux":
            return ".so"
        elif self.os == "macos":
            return ".dylib"
        elif self.os == "windows":
            return ".dll"
        else:
            raise Exception(f"Unknown OS: {self.os}")


def build(target: BuildTarget):
    dl_ext = target.get_dl_ext()
    zig_target = target.compute_zig_target()

    log(f"Building bdwgc{dl_ext} for {zig_target}")

    cmds = [
        *CC,
        "-shared",
        *CFLAGS,
        *SourceFiles,
    ]

    output_dir = Path("./dist").joinpath(target.arch)
    output_dir.mkdir(parents=True, exist_ok=True)

    for dir in IncludeDirs:
        cmds.append("-I")
        cmds.append(dir)

    cmds.append("-target")
    cmds.append(zig_target)
    cmds.append("-o")
    cmds.append(output_dir.joinpath(f"libgc{dl_ext}").as_posix())

    code = subprocess.call(cmds)
    if code != 0:
        log(f"Failed to build bdwgc", level="error")
        exit(1)

    log(f"Finished building bdwgc{dl_ext} for {zig_target}", level="ok")


@contextmanager
def _use_explicit_dir():
    old = os.getcwd()
    try:
        os.chdir(ROOT.as_posix())
        yield
    finally:
        os.chdir(old)


@recipe()
def build_win_x64():
    with _use_explicit_dir():
        build(BuildTarget(arch="x86_64", os="windows"))


@recipe()
def build_macos_x64():
    with _use_explicit_dir():
        build(BuildTarget(arch="x86_64", os="macos"))


@recipe()
def build_linux_x64():
    with _use_explicit_dir():
        build(BuildTarget(arch="x86_64", os="linux"))


make()
