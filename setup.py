#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# flake8: noqa
import io
import os

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import sys
import setuptools

from setuptools.command.develop import develop
from setuptools.command.install import install

here = os.path.abspath(os.path.dirname(__file__))


def read(*names, **kwargs):
    return io.open(
        os.path.join(here, *names),
        encoding=kwargs.get("encoding", "utf8")
    ).read()


long_description = read("README.md")
requirements = read("requirements.txt").split("\n")
optional_requirements = {}

conda_prefix = os.getenv('CONDA_PREFIX')

windows = os.name == 'nt'


def get_pybind_include():
    if windows:
        return os.path.join(conda_prefix, 'Library', 'include')
    return os.path.join(conda_prefix, 'include')


def get_eigen_include():
    if windows:
        return os.path.join(conda_prefix, 'Library', 'include', 'eigen3')
    return os.path.join(conda_prefix, 'include', 'eigen3')


def get_library_dirs():
    if windows:
        return os.path.join(conda_prefix, 'Library', 'lib')
    return os.path.join(conda_prefix, 'lib')


ext_modules = [
    Extension(
        'compas_cgal._cgal',
        sorted([
            'src/compas_cgal.cpp',
            'src/compas.cpp',
            'src/meshing.cpp',
            'src/booleans.cpp',
            'src/slicer.cpp',
            'src/intersections.cpp',
            'src/measure.cpp',
            'src/measuring.cpp',
            'src/triangulations.cpp',
            'src/subdivision.cpp',
        ]),
        include_dirs=[
            './include',
            get_eigen_include(),
            get_pybind_include()
        ],
        library_dirs=[
            get_library_dirs(),
        ],
        libraries=['mpfr', 'gmp'],
        language='c++'
    ),
]

# cf http://bugs.python.org/issue26689
def has_flag(compiler, flagname):
    """Return a boolean indicating whether a flag name is supported on
    the specified compiler.
    """
    import tempfile
    import os
    with tempfile.NamedTemporaryFile('w', suffix='.cpp', delete=False) as f:
        f.write('int main (int argc, char **argv) { return 0; }')
        fname = f.name
    try:
        compiler.compile([fname], extra_postargs=[flagname])
    except setuptools.distutils.errors.CompileError:
        return False
    finally:
        try:
            os.remove(fname)
        except OSError:
            pass
    return True


def cpp_flag(compiler):
    """Return the -std=c++[11/14/17] compiler flag.

    The newer version is prefered over c++11 (when it is available).
    """
    # flags = ['-std=c++17', '-std=c++14', '-std=c++11']
    flags = ['-std=c++14', '-std=c++11']

    for flag in flags:
        if has_flag(compiler, flag):
            return flag

    raise RuntimeError('Unsupported compiler -- at least C++11 support '
                       'is needed!')


class BuildExt(build_ext):
    """A custom build extension for adding compiler-specific options."""
    c_opts = {
        'msvc': ['/EHsc', '/std:c++14'],
        'unix': [],
    }
    l_opts = {
        'msvc': [],
        'unix': [],
    }

    # if sys.platform == 'darwin':
    #     darwin_opts = ['-stdlib=libc++', '-mmacosx-version-min=10.14']
    #     c_opts['unix'] += darwin_opts
    #     l_opts['unix'] += darwin_opts

    def build_extensions(self):
        ct = self.compiler.compiler_type
        opts = self.c_opts.get(ct, [])
        link_opts = self.l_opts.get(ct, [])
        if ct == 'unix':
            opts.append('-DVERSION_INFO="%s"' % self.distribution.get_version())
            opts.append(cpp_flag(self.compiler))
            if has_flag(self.compiler, '-fvisibility=hidden'):
                opts.append('-fvisibility=hidden')
            opts.append('-DCGAL_DEBUG=1')
        for ext in self.extensions:
            ext.define_macros = [('VERSION_INFO', '"{}"'.format(self.distribution.get_version()))]
            ext.extra_compile_args = opts
            ext.extra_link_args = link_opts
        build_ext.build_extensions(self)


setup(
    name="compas_cgal",
    version="0.3.0",
    description="COMPAS friedly bindings for the CGAL library.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/compas-dev/compas_cgal",
    author="tom van mele",
    author_email="van.mele@arch.ethz.ch",
    license="GPL-3 License",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: GPL-3 License",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    keywords=[],
    project_urls={},
    packages=["compas_cgal"],
    package_dir={"": "src"},
    # package_data={},
    # data_files=[],
    # include_package_data=True,
    ext_modules=ext_modules,
    cmdclass={'build_ext': BuildExt},
    setup_requires=['pybind11>=2.5.0'],
    install_requires=requirements,
    python_requires=">=3.6",
    extras_require=optional_requirements,
    zip_safe=False,
)
