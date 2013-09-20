# Copyright (c) 2013 NVIDIA Corporation
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from .interface import NVVMException, NVVMInterface

class ProgramException(Exception):
    def __init__(self, msg):
        self._msg = msg

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.get_message()

    def get_message(self):
        return self._msg


class Program(object):
    """
    An NVVM program object.

    This is a high-level wrapper around the libNVVM program API.
    """

    def __init__(self, lib_name=''):
        self._interface = NVVMInterface(lib_name)
        self._program = self._interface.nvvmCreateProgram()

    def __del__(self):
        if hasattr(self, '_interface'):
            self._interface.nvvmDestroyProgram(self._program)

    def add_module(self, buf, name='<unnamed>'):
        """
        Adds an LLVM IR module `buf` to the program, optionally giving it
        the name `name`.
        """
        self._interface.nvvmAddModuleToProgram(self._program, buf, name)

    def compile(self, options=[]):
        """
        Compiles the program object to PTX using the compiler options
        specified in `options`.
        """
        try:
            self._interface.nvvmCompileProgram(self._program, options)
            ptx = self._interface.nvvmGetCompiledResult(self._program)
            return ptx
        except NVVMException as e:
            log = self._interface.nvvmGetProgramLog(self._program)
            raise ProgramException(log)

    def verify(self, options=[]):
        """
        Verifies the program object using the compiler options specified
        in `options`.
        """
        try:
            self._interface.nvvmVerifyProgram(self._program, options)
        except NVVMException as e:
            log = self._interface.nvvmGetProgramLog(self._program)
            raise ProgramException(log)

