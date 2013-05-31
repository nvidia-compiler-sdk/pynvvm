
import unittest
from util import get_interface

### Low-level interface tests
class CompileTests(unittest.TestCase):
    def test_create_program(self):
        i = get_interface()

        prog = i.nvvmCreateProgram()
        i.nvvmDestroyProgram(prog)

    def test_compile_empty_program(self):
        i = get_interface()

        prog = i.nvvmCreateProgram()
        i.nvvmAddModuleToProgram(prog, """
            target datalayout = "e-p:32:32:32-i1:8:8-i8:8:8-i16:16:16-i32:32:32-i64:64:64-f32:32:32-f64:64:64-v16:16:16-v32:32:32-v64:64:64-v128:128:128-n16:32:64"
            define void @foo() {
                ret void
            }""", 'mymodule')
        i.nvvmCompileProgram(prog, [])
        i.nvvmDestroyProgram(prog)

    def test_verify_empty_program(self):
        i = get_interface()

        prog = i.nvvmCreateProgram()
        i.nvvmAddModuleToProgram(prog, """
            target datalayout = "e-p:32:32:32-i1:8:8-i8:8:8-i16:16:16-i32:32:32-i64:64:64-f32:32:32-f64:64:64-v16:16:16-v32:32:32-v64:64:64-v128:128:128-n16:32:64"
            define void @foo() {
                ret void
            }""", 'mymodule')
        i.nvvmVerifyProgram(prog, [])
        i.nvvmDestroyProgram(prog)

    def test_verify_failure(self):
        import pynvvm.interface
        i = get_interface()

        prog = i.nvvmCreateProgram()
        i.nvvmAddModuleToProgram(prog, """
            target datalayout = "e-p:32:32:32-i1:8:8-i8:8:8-i16:16:16-i32:32:32-i64:64:64-f32:32:32-f64:64:64-v16:16:16-v32:32:32-v64:64:64-v128:128:128-n16:32:64"
            declare void @bar()
            define void @foo() {
                invoke void @bar()
                ret void
            }""", 'mymodule')
        self.assertRaises(pynvvm.interface.NVVMException, i.nvvmVerifyProgram, prog, [])
        i.nvvmDestroyProgram(prog)

    def test_program_log(self):
        import pynvvm.interface
        i = get_interface()

        prog = i.nvvmCreateProgram()
        i.nvvmAddModuleToProgram(prog, """
            target datalayout = "e-p:32:32:32-i1:8:8-i8:8:8-i16:16:16-i32:32:32-i64:64:64-f32:32:32-f64:64:64-v16:16:16-v32:32:32-v64:64:64-v128:128:128-n16:32:64"
            define void @foo() {
                ; No terminator
            }""", 'mymodule')
        self.assertRaises(pynvvm.interface.NVVMException, i.nvvmCompileProgram, prog, [])
        log = i.nvvmGetProgramLog(prog)
        self.assertTrue(len(log) > 0)
        i.nvvmDestroyProgram(prog)        

    def test_program_output(self):
        import pynvvm.interface
        i = get_interface()

        prog = i.nvvmCreateProgram()
        i.nvvmAddModuleToProgram(prog, """
            target datalayout = "e-p:32:32:32-i1:8:8-i8:8:8-i16:16:16-i32:32:32-i64:64:64-f32:32:32-f64:64:64-v16:16:16-v32:32:32-v64:64:64-v128:128:128-n16:32:64"
            define void @foo() {
                ret void
            }""", 'mymodule')
        i.nvvmCompileProgram(prog, [])
        ptx = i.nvvmGetCompiledResult(prog)
        self.assertTrue(len(ptx) > 0)
        i.nvvmDestroyProgram(prog)  
