with open("core/tools/voice_auth.py", "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if not line.startswith("<<<<<<<") and not line.startswith("=======") and not line.startswith(">>>>>>>"):
        new_lines.append(line)

with open("core/tools/voice_auth.py", "w") as f:
    f.writelines(new_lines)
