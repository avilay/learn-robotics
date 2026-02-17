import time

from lerobot.utils.utils import log_say

for i in range(1, 4):
    log_say(f"Recording episode {i}")
    time.sleep(10)
    log_say("Reset the environment")
    time.sleep(3)


log_say("Recording episode one of three")
time.sleep(10)
log_say("Reset the environment")

log_say("Recording episode two of three")
time.sleep(10)
log_say("Reset the environment")

log_say("Recording episode three of three")
time.sleep(10)
log_say("Reset the environment")
