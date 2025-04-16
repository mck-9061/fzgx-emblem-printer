import math
import PIL.Image as Image


def pythag_5d(vector):
    return math.sqrt((vector[0] ** 2) + (vector[1] ** 2) + (vector[2] ** 2) + (vector[3] ** 2) + (vector[4] ** 2))


def pythag_3d(vector):
    return math.sqrt((vector[0] ** 2) + (vector[1] ** 2) + (vector[2] ** 2))


def distance_5d(v1, v2):
    return pythag_5d((v1[0] - v2[0], v1[1] - v2[1], v1[2] - v2[2], v1[3] - v2[3], v1[4] - v2[4]))


def distance(v1, v2):
    return pythag_3d((v1[0] - v2[0], v1[1] - v2[1], v1[2] - v2[2]))


colour_bias = 1.0


def sort_nearest_neighbour(array):
    # Sort an array of type [tuple[tuple[int, int, int], int, int]] by the nearest neighbour
    remaining = [a for a in array]
    # print(remaining)
    done = []

    if len(array) == 0:
        return done

    current = array[0]
    remaining.remove(current)

    while len(remaining) != 0:
        nearest = remaining[0]
        nearestDistance = 99999

        for a in remaining:
            # print(a)
            xyrgb = (a[1], a[2], a[0][0] * colour_bias, a[0][1] * colour_bias, a[0][2] * colour_bias)
            currentXyrgb = (current[1], current[2], current[0][0] * colour_bias, current[0][1] * colour_bias,
                            current[0][2] * colour_bias)

            d = distance_5d(xyrgb, currentXyrgb)
            if d < nearestDistance:
                nearest = a
                nearestDistance = d

        done.append(current)
        current = nearest
        remaining.remove(nearest)

    return done


pre_defined_colours = {}


def initialise_colours():
    global pre_defined_colours
    pre_defined_colours = {
        "red": (232, 24, 32, []),
        "orange": (240, 144, 24, []),
        "yellow": (248, 240, 0, []),
        "light_green": (136, 192, 56, []),
        "green": (56, 176, 72, []),
        "light_blue": (0, 168, 232, []),
        "blue": (0, 80, 160, []),
        "purple": (96, 40, 144, []),
        "pink": (232, 0, 136, []),
        "dark_red": (152, 8, 8, []),
        "gold": (128, 120, 0, []),
        "dark_green": (0, 88, 32, []),
        "dark_blue": (0, 48, 96, []),
        "white": (248, 248, 248, []),
        "grey": (128, 128, 128, []),
        "black": (0, 0, 0, [])
    }


def build_pixels():
    global pre_defined_colours

    im = Image.open("in.png")
    im.thumbnail((62, 62), Image.Resampling.LANCZOS)
    out = Image.new("RGBA", (62, 62), 0xffffff)

    width, height = im.size
    for x in range(width):
        for y in range(height):
            r, g, b, a = im.getpixel((x, y))
            pixel = (r, g, b)

            closest_colour = "black"
            closest_distance = 99999

            if a == 0:
                continue

            for c_name in pre_defined_colours:
                c = pre_defined_colours[c_name]
                d = distance(c, pixel)
                if d <= closest_distance:
                    closest_distance = d
                    closest_colour = c_name

            pre_defined_colours[closest_colour][3].append((pixel, x, y))

    x = 0
    y = 0
    for c_name in pre_defined_colours:
        pre_defined_colours[c_name] = (
            pre_defined_colours[c_name][0], pre_defined_colours[c_name][1], pre_defined_colours[c_name][2],
            sort_nearest_neighbour(pre_defined_colours[c_name][3]))

        for pixel in pre_defined_colours[c_name][3]:
            # print(pixel)
            toWrite = (pixel[0][0], pixel[0][1], pixel[0][2], 255)

            out.putpixel((pixel[1], pixel[2]), toWrite)
            x += 1
            if x == im.width:
                x = 0
                y += 1

    out.save("out.png")


def move_cursor(current, target, outFile):
    while target[0] != current[0]:
        if target[0] < current[0]:
            outFile.write("left\n")
            current[0] -= 1
        else:
            outFile.write("right\n")
            current[0] += 1

    while target[1] != current[1]:
        if target[1] < current[1]:
            outFile.write("up\n")
            current[1] -= 1
        else:
            outFile.write("down\n")
            current[1] += 1


# rgb param: 0 = red, 1 = green, 2 = blue
def move_rgb_slider(colour_cursor, rgb, current, target, outFile):
    if current[rgb] != target[rgb]:
        while colour_cursor[2] != 0:
            outFile.write("cup\n")
            colour_cursor[2] -= 1

        while colour_cursor[0] != rgb:

            if colour_cursor[0] > rgb:
                outFile.write("cdown\n")
                colour_cursor[0] -= 1
            else:
                outFile.write("cup\n")
                colour_cursor[0] += 1

        j = 1
        while current[rgb] > target[rgb]:
            outFile.write("cleft\n")
            current[rgb] -= 1
            j += 1
            if j % 4 == 0:
                j = 1
                outFile.write("cup\n")
                outFile.write("cdown\n")

        j = 1
        while current[rgb] < target[rgb]:
            outFile.write("cright\n")
            current[rgb] += 1
            j += 1
            if j % 4 == 0:
                j = 1
                outFile.write("cup\n")
                outFile.write("cdown\n")


def build_sequence():
    global pre_defined_colours

    out = open("out.txt", "w+", encoding="utf-8")

    set_selected_colour = ["a", "x", "b", "right", "a", "a", "b", "left", "a"]

    pixels_remaining = sum([len(pre_defined_colours[a][3]) for a in pre_defined_colours])
    out.write("-remaining: " + str(pixels_remaining) + "\n")

    # Set up
    # Set brush size
    out.write("z\n")
    out.write("z\n")
    out.write("z\n")

    out.write("a\n")

    # Move to top left
    for i in range(32):
        out.write("up\n")
        out.write("left\n")

    c_id = -1
    cursor = [0, 0]
    # Index 0: 0 = red, 1 = green, 2 = blue, 3 = Pre-defined section
    colour_cursor = [3, 0, 0]

    for c_name in pre_defined_colours:
        out.write("---------------" + c_name + "---------------\n")

        c_id += 1

        if len(pre_defined_colours[c_name][3]) == 0:
            continue

        # Move to first pixel
        pixel1 = pre_defined_colours[c_name][3][0]
        x = pixel1[1]
        y = pixel1[2]

        target_cursor = (x, y)
        move_cursor(cursor, target_cursor, out)

        # Move to pre-defined colour section
        while colour_cursor[0] != 3:
            out.write("cdown\n")
            colour_cursor[0] += 1

        # Move to target cursor
        target_cursor = (c_id % 4, c_id // 4)

        while target_cursor[0] != colour_cursor[1]:
            if target_cursor[0] < colour_cursor[1]:
                out.write("cleft\n")
                colour_cursor[1] -= 1
            else:
                out.write("cright\n")
                colour_cursor[1] += 1

        while target_cursor[1] != colour_cursor[2]:
            if target_cursor[1] < colour_cursor[2]:
                out.write("cup\n")
                colour_cursor[2] -= 1
            else:
                out.write("cdown\n")
                colour_cursor[2] += 1

        # Select colour
        for m in set_selected_colour:
            out.write(m + "\n")

        current_rgb = [pre_defined_colours[c_name][0], pre_defined_colours[c_name][1], pre_defined_colours[c_name][2]]

        # Draw each pixel
        for pixel in pre_defined_colours[c_name][3]:
            rgb = pixel[0]
            x = pixel[1]
            y = pixel[2]

            # Adjust RGB sliders
            move_rgb_slider(colour_cursor, 0, current_rgb, rgb, out)
            move_rgb_slider(colour_cursor, 1, current_rgb, rgb, out)
            move_rgb_slider(colour_cursor, 2, current_rgb, rgb, out)

            # Move to target cursor
            target_cursor = (x, y)
            move_cursor(cursor, target_cursor, out)

            # Draw
            out.write("a\n")
            pixels_remaining -= 1

            out.write("-remaining: " + str(pixels_remaining) + "\n")

    out.close()


def decimal_range(start, stop, increment):
    while start < stop:
        yield start
        start += increment


def determine_best_bias():
    global colour_bias

    initialise_colours()

    lowestLines = 999999999
    bestBias = 1.0

    for i in decimal_range(0.9, 3.0, 0.01):
        colour_bias = i

        initialise_colours()

        build_pixels()
        build_sequence()
        f = open("out.txt", "r", encoding="utf-8").readlines()
        print("Bias " + str(i) + ": " + str(len(f)))

        if len(f) < lowestLines:
            lowestLines = len(f)
            bestBias = i

    print("Best bias is " + str(bestBias) + " at " + str(lowestLines) + " steps")

    return bestBias


# colour_bias = determine_best_bias()
colour_bias = 1.7

initialise_colours()

print("Building pixels...")
build_pixels()
print("Building sqeuence...")
build_sequence()

print("Done")
