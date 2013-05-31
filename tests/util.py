
import os

def get_interface():
    import pynvvm.interface
    # Grab the libnvvm location from the environment
    if 'LIBNVVM_BINARY' in os.environ:
        return pynvvm.interface.NVVMInterface(os.environ['LIBNVVM_BINARY'])
    else:
        return pynvvm.interface.NVVMInterface()
