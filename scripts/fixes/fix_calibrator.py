with open("core/emotion/calibrator.py", "r") as f:
    content = f.read()

content = content.replace("<<<<<<< HEAD", "")
content = content.replace("=======", "")
content = content.replace(">>>>>>> origin/jules-3466090822907057400-4af64808", "")
content = content.replace("self._baseline_mgr = EmotionBaselineManagercalibration_duration_seconds=30)", "")

with open("core/emotion/calibrator.py", "w") as f:
    f.write(content)
