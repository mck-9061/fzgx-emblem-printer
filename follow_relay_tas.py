import time
import serial
import cv2
import PIL.Image as Image
from collections import deque

port = serial.Serial('COM24', 115200);

buttons = {
    "a": b'\x11',
    "up": b'\x08',
    "down": b'\x05',
    "left": b'\x07',
    "right": b'\x06',
    "cup": b'\x10',
    "cdown": b'\x12',
    "cleft": b'\x09',
    "cright": b'\x0E'
}

# with mss() as sct:
#     monitor = {'top': 280, 'left': 1022, 'width': 515, 'height': 515, 'mon': 1}
#
#     # Grab the data
#     sct_img = sct.grab(monitor)
#
#     output = "sct-mon{mon}_{top}x{left}_{width}x{height}.png".format(**monitor)
#     tools.to_png(sct_img.rgb, sct_img.size, output=output)
#
#     out = Image.new("RGBA", (62, 62), 0xffffff)
#
#     for x in range(0, 62):
#         for y in range(0, 62):
#             print(str(x) + ", " + str(y))
#
#             left_shifts = x // 3
#             up_shifts = y // 3
#
#             pixel = sct_img.pixel(4 + (8 * x) + left_shifts, 4 + (8 * y) + up_shifts)
#             print(pixel)
#             out.putpixel((x, y), (pixel[0], pixel[1], pixel[2], 255))
#
#     out.save("test.png")

def move_rgb_slider(colour_cursor, rgb, current, target, out):
    if current[rgb] != target[rgb]:

        while colour_cursor[2] != 0:
            out.append("cup")
            colour_cursor[2] -= 1

        while colour_cursor[0] != rgb:

            if colour_cursor[0] < rgb:
                out.append("cdown")
                colour_cursor[0] += 1
            else:
                out.append("cup")
                colour_cursor[0] -= 1

        j = 1
        while current[rgb] > target[rgb]:
            out.append("cleft")
            current[rgb] -= 1
            j += 1
            if j % 4 == 0:
                j = 1
                out.append("cdown")
                out.append("cup")

        j = 1
        while current[rgb] < target[rgb]:
            out.append("cright")
            current[rgb] += 1
            j += 1
            if j % 4 == 0:
                j = 1
                out.append("cdown")
                out.append("cup")

def move_cursor(current, target, out):
    while target[0] != current[0]:
        if target[0] < current[0]:
            out.append("left")
            current[0] -= 1
        else:
            out.append("right")
            current[0] += 1

    while target[1] != current[1]:
        if target[1] < current[1]:
            out.append("up")
            current[1] -= 1
        else:
            out.append("down")
            current[1] += 1

expected_colour_cursor = 2
delay = 0.12

# Setup camera
cap = cv2.VideoCapture(5)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 2560)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1440)

x_offset = 907
y_offset = 322

while True:
    a = input("Enter 'd' to enter button mode, enter 'y' to begin TAS: ")

    if a == "d":
        while True:
            c = input("In button mode. Enter button: ")
            port.write(buttons[c])
            time.sleep(0.09)

    if a == "y":
        sequence = deque(open("out.txt", "r", encoding="utf-8").readlines())

        print("Estimated time: " + str(int(len(sequence) * 0.08) * 2) + " seconds")

        currentPixel = ""
        nextCurrentPixel = ""

        while len(sequence) != 0:
            l = sequence.popleft()
            line = l.strip()
            if l.startswith("-"):
                if l.startswith("-e"):
                    expected_colour_cursor = int(l.replace("-e", "").strip())

                if l.startswith("-p"):
                    if currentPixel == "":
                        # First pixel
                        currentPixel = l.replace("-p", "").strip()
                    else:
                        print("Checking pixel...")
                        port.write(b'\x06')
                        time.sleep(0.5)
                        x = int(currentPixel.split(",")[3])
                        y = int(currentPixel.split(",")[4])

                        cap.read()
                        ret, frame = cap.read()

                        right_shifts = x // 31
                        down_shifts = y // 31

                        readPixel = frame[6 + (12 * y) + down_shifts + y_offset, 6 + (12 * x) + right_shifts + x_offset]
                        pixel = (int(readPixel[2]), int(readPixel[1]), int(readPixel[0]))

                        print(pixel)
                        print(currentPixel)

                        totalDifference = abs(pixel[0] - int(currentPixel.split(",")[0])) + abs(pixel[1] - int(currentPixel.split(",")[1])) + abs(pixel[2] - int(currentPixel.split(",")[2]))

                        if totalDifference > 25:
                            print("Desync! Resetting cursors and replotting last pixel.")

                            # Save captured image
                            out = Image.new("RGBA", (62, 62), 0xffffff)

                            for x2 in range(0, 62):
                                for y2 in range(0, 62):
                                    #print(str(x2) + ", " + str(y2))

                                    left_shifts = x2 // 31
                                    up_shifts = y2 // 31

                                    pixel = frame[
                                        6 + (12 * y2) + up_shifts + y_offset, 6 + (12 * x2) + left_shifts + x_offset]
                                    #print(pixel)
                                    out.putpixel((x2, y2), (pixel[2], pixel[1], pixel[0], 255))

                            out.save("fail.png")

                            for i in range(75):
                                port.write(buttons["up"])
                                time.sleep(delay)
                                port.write(buttons["left"])
                                time.sleep(delay)

                            for i in range(6):
                                port.write(buttons["cup"])
                                time.sleep(delay)

                            for i in range(40):
                                port.write(buttons["cleft"])
                                time.sleep(delay)

                            port.write(buttons["cdown"])
                            for i in range(40):
                                port.write(buttons["cleft"])
                                time.sleep(delay)

                            port.write(buttons["cdown"])
                            for i in range(40):
                                port.write(buttons["cleft"])
                                time.sleep(delay)

                            port.write(buttons["cup"])
                            time.sleep(delay)
                            port.write(buttons["cdown"])

                            port.write(buttons["a"])
                            time.sleep(delay)
                            print("Cursor at top left, all colours at 0, colour cursor on blue. Replotting last pixel.")

                            cursor = [0, 0]
                            colour_cursor = [2, 0, 0]
                            current_rgb = [0, 0, 0]
                            rgb = (int(currentPixel.split(",")[0]), int(currentPixel.split(",")[1]), int(currentPixel.split(",")[2]))
                            slider_moves = []
                            cursor_moves = []

                            # Adjust RGB sliders
                            move_rgb_slider(colour_cursor, 0, current_rgb, rgb, slider_moves)
                            move_rgb_slider(colour_cursor, 1, current_rgb, rgb, slider_moves)
                            move_rgb_slider(colour_cursor, 2, current_rgb, rgb, slider_moves)

                            # Move to target cursor
                            target_cursor = (x, y)
                            move_cursor(cursor, target_cursor, cursor_moves)

                            fixing_moves = []

                            # Write
                            k = 0
                            for slider_move in slider_moves:
                                if k < len(cursor_moves):
                                    fixing_moves.append(slider_move + "," + cursor_moves[k] + "\n")
                                else:
                                    fixing_moves.append(slider_move + "\n")

                                k += 1

                            while k < len(cursor_moves):
                                fixing_moves.append(cursor_moves[k] + "\n")
                                k += 1

                            if colour_cursor[0] != expected_colour_cursor:
                                while colour_cursor[0] > expected_colour_cursor:
                                    fixing_moves.append("cup\n")
                                    colour_cursor[0] -= 1

                                while colour_cursor[0] < expected_colour_cursor:
                                    fixing_moves.append("cdown\n")
                                    colour_cursor[0] += 1

                            # Draw
                            fixing_moves.append("a\n")

                            sequence.appendleft("-p" + currentPixel)
                            sequence.appendleft("-fixed")
                            for a in reversed(fixing_moves):
                                print(a)
                                sequence.appendleft(a)

                            sequence.appendleft("-fixing")
                            if nextCurrentPixel == "":
                                nextCurrentPixel = l.replace("-p", "").strip()
                        else:
                            print("Good")

                            if nextCurrentPixel != "":
                                currentPixel = nextCurrentPixel
                                nextCurrentPixel = ""
                            else:
                                currentPixel = l.replace("-p", "").strip()

                            port.write(b'\x07')
                            time.sleep(delay)

                print(line)
                continue

            toPress = [buttons[a] for a in line.split(",")]

            if len(toPress) > 1:
                port.write(b'\x7A')
                time.sleep(0.01)

            for key in toPress:
                port.write(key)
                time.sleep(0.01)

            time.sleep(delay)


