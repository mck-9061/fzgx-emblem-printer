import cv2
import PIL.Image as Image

# Setup camera
cap = cv2.VideoCapture(5)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 2560)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1440)

# Capture frame
ret, frame = cap.read()

out = Image.new("RGBA", (62, 62), 0xffffff)

x_offset = 907
y_offset = 322

for x in range(0, 62):
    for y in range(0, 62):
        print(str(x) + ", " + str(y))

        left_shifts = x // 31
        up_shifts = y // 31

        pixel = frame[6 + (12 * y) + up_shifts + y_offset, 6 + (12 * x) + left_shifts + x_offset]
        print(pixel)
        out.putpixel((x, y), (pixel[2], pixel[1], pixel[0], 255))

out.save("test.png")