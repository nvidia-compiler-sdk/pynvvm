import nose
import os

if 'LIBNVVM_BINARY' not in os.environ:
    print('WARNING: LIBNVVM_BINARY is not set, libnvvm may not be found!')

os.chdir('tests')
nose.run()
