import nose
import os

if 'LIBNVVM_BINARY' not in os.environ:
    print('WARNING: LIBNVVM_BINARY is not set, assuming it is in [DY]LD_LIBRARY_PATH/PATH')

os.chdir('tests')
nose.run()
