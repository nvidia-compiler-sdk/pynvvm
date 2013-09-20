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


from ctypes import (
    POINTER,
    c_int,
    c_void_p,
    byref,
    create_string_buffer,
    c_char_p,
    c_size_t,
    sizeof,
    cdll,
)
from platform import system

# libNVVM status codes
NVVM_SUCCESS = 0
NVVM_ERROR_OUT_OF_MEMORY = 1
NVVM_ERROR_PROGRAM_CREATION_FAILURE = 2
NVVM_ERROR_IR_VERSION_MISMATCH = 3
NVVM_ERROR_INVALID_INPUT = 4
NVVM_ERROR_INVALID_PROGRAM = 5
NVVM_ERROR_INVALID_IR = 6
NVVM_ERROR_INVALID_OPTION = 7
NVVM_ERROR_NO_MODULE_IN_PROGRAM = 8
NVVM_ERROR_COMPILATION = 9


class NVVMException(Exception):
    """
    Exception wrapper for libNVVM error codes.
    """
    def __init__(self, msg):
        Exception.__init__(self)
        self._msg = msg

    def __str__(self):
        return 'NVVM Error: %s' % self._msg

    def __repr__(self):
        return str(self)



class NVVMInterface(object):
    """
    Low-level interface to libNVVM. This class is primarily designed for
    interfacing the high-level API with the libNVVM binary, but clients
    are free to use libNVVM directly through this class.
    """
    def __init__(self, lib_path=''):
        self._lib = None
        self._load_nvvm_lib(lib_path)

    def _load_nvvm_lib(self, lib_path):
        """
        Loads the libNVVM shared library, with an optional search path in
        lib_path.
        """
        if system() == 'Windows':
            if sizeof(c_void_p) == 8:
                def_lib_name = 'nvvm64_20_0.dll'
            else:
                def_lib_name = 'nvvm32_20_0.dll'
        elif system() == 'Darwin':
            def_lib_name = 'libnvvm.dylib'
        else:
            def_lib_name = 'libnvvm.so'

        if len(lib_path) == 0:
            name = def_lib_name
        else:
            name = lib_path

        self._lib = cdll.LoadLibrary(name)

        self._lib.nvvmCreateProgram.argtypes = [ POINTER(c_void_p) ]
        self._lib.nvvmCreateProgram.restype = c_int

        self._lib.nvvmDestroyProgram.argtypes = [ POINTER(c_void_p) ]
        self._lib.nvvmDestroyProgram.restype = c_int

        self._lib.nvvmAddModuleToProgram.argtypes = [
            c_void_p,
            c_char_p,
            c_size_t,
            c_char_p
        ]
        self._lib.nvvmAddModuleToProgram.restype = c_int

        self._lib.nvvmVerifyProgram.argtypes = [
            c_void_p,
            c_int, POINTER(c_char_p)
        ]
        self._lib.nvvmVerifyProgram.restype = c_int

        self._lib.nvvmCompileProgram.argtypes = [
            c_void_p,
            c_int,
            POINTER(c_char_p)
        ]
        self._lib.nvvmCompileProgram.restype = c_int

        self._lib.nvvmGetCompiledResultSize.argtypes = [
            c_void_p,
            POINTER(c_size_t)
        ]
        self._lib.nvvmGetCompiledResultSize.restype = c_int

        self._lib.nvvmGetCompiledResult.argtypes = [ c_void_p, c_char_p ]
        self._lib.nvvmGetCompiledResult.restype = c_int

        self._lib.nvvmGetProgramLogSize.argtypes = [
            c_void_p,
            POINTER(c_size_t)
        ]
        self._lib.nvvmGetProgramLogSize.restype = c_int

        self._lib.nvvmGetProgramLog.argtypes = [ c_void_p, c_char_p ]
        self._lib.nvvmGetProgramLog.restype = c_int

        self._lib.nvvmGetErrorString.argtypes = [ c_int ]
        self._lib.nvvmGetErrorString.restype = c_char_p

        self._lib.nvvmVersion.argtypes = [ POINTER(c_int), POINTER(c_int) ]
        self._lib.nvvmVersion.restype = c_int

    def _throw_on_error(self, code):
        """
        Raises an NVVMException is the given code is not NVVM_SUCCESS.
        """
        if code == NVVM_SUCCESS:
            return
        else:
            raise NVVMException(self.nvvmGetErrorString(code))

    def nvvmCreateProgram(self):
        """
        Creates and returns a new NVVM program object.
        """
        res = c_void_p()
        code = self._lib.nvvmCreateProgram(byref(res))
        self._throw_on_error(code)
        return res
        
    def nvvmDestroyProgram(self, prog):
        """
        Destroys the given NVVM program object.
        """
        code = self._lib.nvvmDestroyProgram(byref(prog))
        self._throw_on_error(code)
        return

    def nvvmAddModuleToProgram(self, prog, buf, name):
        """
        Adds an LLVM IR module to the given NVVM program object.

        The LLVM IR can be either a text LL buffer or a bitcode buffer.
        """
        raw_buf = create_string_buffer(buf, len(buf))
        name_buf = create_string_buffer(name)
        code = self._lib.nvvmAddModuleToProgram(prog, raw_buf,
            c_size_t(len(buf)), name_buf)
        self._throw_on_error(code)
        return

    def nvvmVerifyProgram(self, prog, options):
        """
        Verifies that the NVVM program object is made up of well-formed NVVM IR
        objects. Raises an NVVMException if not.
        """
        options_array = (c_char_p * len(options))()
        options_array[:] = options
        code = self._lib.nvvmVerifyProgram(prog, len(options), options_array)
        self._throw_on_error(code)
        return

    def nvvmCompileProgram(self, prog, options):
        """
        Compiles the NVVM program object into PTX, using the provided options
        array.  See the libNVVM API documentation for accepted options.
        """
        options_array = (c_char_p * len(options))()
        options_array[:] = options
        code = self._lib.nvvmCompileProgram(prog, len(options), options_array)
        self._throw_on_error(code)
        return

    def nvvmGetCompiledResult(self, prog):
        """
        Returns the compiled PTX for the NVVM program object.
        """
        size = c_size_t()
        code = self._lib.nvvmGetCompiledResultSize(prog, byref(size))
        self._throw_on_error(code)

        buf = create_string_buffer(size.value)
        code = self._lib.nvvmGetCompiledResult(prog, buf)
        self._throw_on_error(code)

        return buf.value.decode('utf-8')

    def nvvmGetProgramLog(self, prog):
        """
        Returns the log for the NVVM program object.

        Only useful after calls to nvvmCompileProgram or nvvmVerifyProgram.
        """
        size = c_size_t()
        code = self._lib.nvvmGetProgramLogSize(prog, byref(size))
        self._throw_on_error(code)

        buf = create_string_buffer(size.value)
        code = self._lib.nvvmGetProgramLog(prog, buf)
        self._throw_on_error(code)

        return buf.value.decode('utf-8')

    def nvvmGetErrorString(self, code):
        """
        Returns a text identifier for the given NVVM status code.
        """
        code_int = c_int(code)
        res = self._lib.nvvmGetErrorString(code_int)
        return res.decode('utf-8')

    def nvvmVersion(self):
        """
        Returns the loaded libNVVM library version as a (major, minor) tuple.
        """
        major = c_int()
        minor = c_int()
        code = self._lib.nvvmVersion(byref(major), byref(minor))
        self._throw_on_error(code)
        return (major.value, minor.value)

    def __str__(self):
        (major, minor) = self.nvvmVersion()
        return 'NVVM Interface (Version: %d.%d)' % (major, minor)

    def __repr__(self):
        return str(self)
