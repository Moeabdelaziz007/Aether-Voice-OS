with open("core/ai/thalamic.py", "r") as f:
    content = f.read()

content = content.replace("<<<<<<< HEAD", "")
content = content.replace("=======", "")
content = content.replace(">>>>>>> origin/jules-3466090822907057400-4af64808", "")
content = content.replace("self._calibrator = EmotionCalibrator)", "self._calibrator = EmotionCalibrator()")
content = content.replace("self._metrics = Demometrics)", "self._metrics = DemoMetrics()")

with open("core/ai/thalamic.py", "w") as f:
    f.write(content)
