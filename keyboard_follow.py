import pydirectinput
import time

buttons = {
    "a": "a",
    "b": "n",
    "up": "up",
    "down": "down",
    "left": "left",
    "right": "right",
    "cup": "t",
    "cdown": "g",
    "cleft": "f",
    "cright": "h"
}

pydirectinput.PAUSE = 0

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

    toPress = [buttons[a] for a in line.split(",")]

    for key in toPress:
        pydirectinput.keyDown(key)

    time.sleep(0.033)

    for key in toPress:
        pydirectinput.keyUp(key)

    time.sleep(0.033)

    #pydirectinput.hotkey(*toPress, interval=0.033, wait=0.0)
