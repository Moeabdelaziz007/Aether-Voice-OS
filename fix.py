with open("core/audio/capture.py", "r") as f:
    content = f.read()

# Fix the first conflict around line 80
import re

first_conflict = re.search(r'<<<<<<< HEAD\n(.*?)\n=======', content, re.DOTALL)
if first_conflict:
    print("Found first conflict properly formatted... wait, it lacks ======= and >>>>>>> ?")
