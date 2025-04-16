import pydirectinput
import time

buttons = {
    "a": "a",
    "b": "n",
    "x": "b",
    "z": "/",
    "up": "up",
    "down": "down",
    "left": "left",
    "right": "right",
    "cup": "t",
    "cdown": "g",
    "cleft": "f",
    "cright": "h"
}

delay = 0.1
pydirectinput.PAUSE = 0.033

print("Starting in 5...")
time.sleep(5)
print("Starting.")

sequence = open("out.txt", "r", encoding="utf-8").readlines()

print("Estimated time: " + str(int(len(sequence) * 0.033) * 2) + " seconds")

for l in sequence:
    line = l.strip()
    if l.startswith("-"):
        print(line)
        continue

    pydirectinput.press(buttons[line])
    #time.sleep(delay)
