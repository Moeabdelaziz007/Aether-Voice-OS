with open("core/tools/tasks_tool.py", "r") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if not line.startswith("<<<<<<<") and not line.startswith("=======") and not line.startswith(">>>>>>>"):
        new_lines.append(line)

with open("core/tools/tasks_tool.py", "w") as f:
    f.writelines(new_lines)
