with open("infra/scripts/benchmark.py", "r") as f:
    content = f.read()

s1 = """import sys
<<<<<<< ours
=======
import time
>>>>>>> theirs
from pathlib import Path"""

r1 = """import sys
import time
from pathlib import Path"""

content = content.replace(s1, r1)

with open("infra/scripts/benchmark.py", "w") as f:
    f.write(content)
