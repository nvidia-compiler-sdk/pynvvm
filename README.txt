
===================================
pynvvm - Python Bindings to libNVVM
===================================


Introduction
============

The pynvvm package is a Python binding for the libNVVM compiler library from
NVIDIA.  This library takes LLVM (NVVM) IR input and produces NVIDIA PTX
output suitable for execution on NVIDIA GPUs on any platform.  Please see the
CUDA 5.5 documentation for a complete description of libNVVM.


Installation
============

The pynvvm package does not have any external dependencies and can be
installed with ``pip`` or ``easy_install``.

    $ pip install pynvvm


Using pynvvm
============

There are two primary interfaces with pynvvm; a low-level interface exists
which provides users with direct access to the libNVVM API, and a high-level
interface provides a Pythonic API for libNVVM.


Low-Level Interface
-------------------

The low-level interface can be found in the ``pynvvm.interface`` module. An
instance of the interface can be obtained by calling the ``NVVMInterface``
constructor:

    from pynvvm.interface import NVVMInterface

    inter = NVVMInterface()

By default, the ``NVVMInterface`` object will attempt to load the libNVVM
shared library from ``LD_LIBRARY_PATH`` on Linux, ``DYLD_LIBRARY_PATH`` on
Mac, or ``PATH`` on Windows.  An optional parameter to the ``NVVMInterface``
constructor provides the absolute path to the libNVVM shared library and
overwrites the system search path.  For example, on Linux:

    from pynvvm.interface import NVVMInterface

    inter = NVVMInterface('/usr/local/cuda-5.5/nvvm/lib64/libnvvm.so')

Once an interface object is created, it provides access to all of the libNVVM
API functions as regular Python functions. However, instead of returning a
libNVVM status code, each function returns either a string (for output
functions) or None.  If an error occurs within libNVVM, an ``NVVMException``
exception is raised with the corresponding status code.

Note that the ``nvvmGetProgramLogSize`` and ``nvvmGetCompiledResultSize``
functions are *not* exposed.  Instead, the ``nvvmGetProgramLog`` and
``nvvmGetCompiledResult`` functions automatically determine the correct size
and return a UTF-8 encoded Python string.

Full Example:

    from pynvvm.interface import NVVMInterface, NVVMException

    module = ...

    inter = NVVMInterface()
    prog = inter.nvvmCreateProgram()
    try:
        inter.nvvmAddModuleToProgram(prog, module, 'mymodule')
        inter.nvvmCompileProgram(prog, ['-ftz=1'])
        ptx = inter.nvvmGetCompiledResult(prog)
    except NVVMException as e:
        print('Error: %s' % repr(e))



High-Level Interface
--------------------

For clients wanting a higher-level interface to libNVVM, the ``Program`` class
in ``pynvvm.compiler`` provides such an interface.
