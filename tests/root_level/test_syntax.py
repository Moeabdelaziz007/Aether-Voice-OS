import compileall
import sys

compiled = compileall.compile_dir('core/', quiet=1)
if not compiled:
    sys.exit(1)
