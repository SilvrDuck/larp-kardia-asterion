On macos, need to go to `venv...lib/python3.7/site-packages/pyttsx3/drivers/nsss.py` and change line `self = super(NSSpeechDriver, self).init()` to `eslf = objc.super(NSSpeechDriver, self).init()`.