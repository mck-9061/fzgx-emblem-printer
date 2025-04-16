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
            xyrgb = (a[1], a[2], a[0][0]*colour_bias, a[0][1]*colour_bias, a[0][2]*colour_bias)
            currentXyrgb = (current[1], current[2], current[0][0]*colour_bias, current[0][1]*colour_bias, current[0][2]*colour_bias)

            d = distance_5d(xyrgb, currentXyrgb)
            if d < nearestDistance:
                nearest = a
                nearestDistance = d

        done.append(current)
        current = nearest
        remaining.remove(nearest)

    return done


pre_defined_colours = {
    "blank": (0, 0, 0, []),
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
    im = Image.open("in.png")
    im.thumbnail((62, 62), Image.Resampling.LANCZOS)
    out = Image.new("RGBA", (62, 62), 0xffffff)

    width, height = im.size
    for x in range(width):
        for y in range(height):
            r, g, b, a = im.getpixel((x, y))
            pixel = (r, g, b)

            closest_match = (0, 0, 0)
            closest_colour = "black"
            closest_distance = 99999

            if a == 0:
                pre_defined_colours["blank"][3].append((pixel, x, y))
                continue

            for c_name in pre_defined_colours:
                c = pre_defined_colours[c_name]
                d = distance(c, pixel)
                if d <= closest_distance:
                    closest_distance = d
                    closest_match = c
                    closest_colour = c_name

            pre_defined_colours[closest_colour][3].append((pixel, x, y))

    x = 0
    y = 0
    for c_name in pre_defined_colours:
        #print(c_name)

        if not c_name == "blank":
            pre_defined_colours[c_name] = (pre_defined_colours[c_name][0], pre_defined_colours[c_name][1], pre_defined_colours[c_name][2], sort_nearest_neighbour(pre_defined_colours[c_name][3]))

        for pixel in pre_defined_colours[c_name][3]:
            # print(pixel)
            toWrite = (pixel[0][0], pixel[0][1], pixel[0][2], 255)
            if c_name == "blank":
                toWrite = (pixel[0][0], pixel[0][1], pixel[0][2], 0)

            out.putpixel((pixel[1], pixel[2]), toWrite)
            x += 1
            if x == im.width:
                x = 0
                y += 1

    out.save("out.png")


def build_sequence():
    out = open("out.txt", "w+", encoding="utf-8")

    set_selected_colour = ["a", "x", "b", "right", "a", "a", "b", "left", "a"]

    pixels_remaining = sum([len(pre_defined_colours[a][3]) for a in pre_defined_colours if a != "blank"])
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
    current_rgb = [0, 0, 0]
    # Index 0: 0 = R, 1 = G, 2 = B, 3 = Pre-defined section
    colour_cursor = [3, 0, 0]
    for c_name in pre_defined_colours:
        #print(c_name)
        if c_name == "blank":
            continue

        out.write("---------------" + c_name + "---------------\n")

        c_id += 1

        if not len(pre_defined_colours[c_name][3]) == 0:
            # Move to first pixel
            pixel1 = pre_defined_colours[c_name][3][0]
            x = pixel1[1]
            y = pixel1[2]

            target_cursor = (x, y)

            while target_cursor[0] != cursor[0]:
                if target_cursor[0] < cursor[0]:
                    out.write("left\n")
                    cursor[0] -= 1
                else:
                    out.write("right\n")
                    cursor[0] += 1

            while target_cursor[1] != cursor[1]:
                if target_cursor[1] < cursor[1]:
                    out.write("up\n")
                    cursor[1] -= 1
                else:
                    out.write("down\n")
                    cursor[1] += 1

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

            if rgb[0] != current_rgb[0]:
                # Move red slider
                while colour_cursor[0] != 0:
                    out.write("cup\n")
                    if colour_cursor[2] != 0:
                        colour_cursor[2] -= 1
                    else:
                        colour_cursor[0] -= 1

                j = 1
                while current_rgb[0] > rgb[0]:
                    out.write("cleft\n")
                    current_rgb[0] -= 1
                    j += 1
                    if j % 5 == 0:
                        j = 1
                        out.write("cdown\n")
                        out.write("cup\n")

                j = 1
                while current_rgb[0] < rgb[0]:
                    out.write("cright\n")
                    current_rgb[0] += 1
                    j += 1
                    if j % 5 == 0:
                        j = 1
                        out.write("cdown\n")
                        out.write("cup\n")

            if rgb[1] != current_rgb[1]:
                # Move green slider
                while colour_cursor[0] != 1:
                    if colour_cursor[0] == 0:
                        out.write("cdown\n")
                        colour_cursor[0] = 1
                    else:
                        out.write("cup\n")
                        if colour_cursor[2] != 0:
                            colour_cursor[2] -= 1
                        else:
                            colour_cursor[0] -= 1

                j = 1
                while current_rgb[1] > rgb[1]:
                    out.write("cleft\n")
                    current_rgb[1] -= 1
                    j += 1
                    if j % 5 == 0:
                        j = 1
                        out.write("cdown\n")
                        out.write("cup\n")

                j = 1
                while current_rgb[1] < rgb[1]:
                    out.write("cright\n")
                    current_rgb[1] += 1
                    j += 1
                    if j % 4 == 0:
                        j = 1
                        out.write("cdown\n")
                        out.write("cup\n")

            if rgb[2] != current_rgb[2]:
                # Move blue slider
                while colour_cursor[0] != 2:
                    if colour_cursor[0] == 0:
                        out.write("cdown\n")
                        out.write("cdown\n")
                        colour_cursor[0] = 2
                    elif colour_cursor[0] == 1:
                        out.write("cdown\n")
                        colour_cursor[0] = 2
                    else:
                        out.write("cup\n")
                        if colour_cursor[2] != 0:
                            colour_cursor[2] -= 1
                        else:
                            colour_cursor[0] -= 1

                j = 1
                while current_rgb[2] > rgb[2]:
                    out.write("cleft\n")
                    current_rgb[2] -= 1
                    j += 1
                    if j % 4 == 0:
                        j = 1
                        out.write("cup\n")
                        out.write("cdown\n")

                j = 1
                while current_rgb[2] < rgb[2]:
                    out.write("cright\n")
                    current_rgb[2] += 1
                    j += 1
                    if j % 4 == 0:
                        j = 1
                        out.write("cup\n")
                        out.write("cdown\n")

            # Move to target cursor
            target_cursor = (x, y)

            while target_cursor[0] != cursor[0]:
                if target_cursor[0] < cursor[0]:
                    out.write("left\n")
                    cursor[0] -= 1
                else:
                    out.write("right\n")
                    cursor[0] += 1

            while target_cursor[1] != cursor[1]:
                if target_cursor[1] < cursor[1]:
                    out.write("up\n")
                    cursor[1] -= 1
                else:
                    out.write("down\n")
                    cursor[1] += 1

            # Draw
            out.write("a\n")
            pixels_remaining -= 1

            out.write("-remaining: " + str(pixels_remaining) + "\n")

    out.close()


def decimal_range(start, stop, increment):
    while start < stop:
        yield start
        start += increment

lowestLines = 999999999
bestBias = 1.0


for i in decimal_range(0.9, 3.0, 0.01):
    colour_bias = i

    pre_defined_colours = {
        "blank": (0, 0, 0, []),
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

    build_pixels()
    build_sequence()
    f = open("out.txt", "r", encoding="utf-8").readlines()
    print("Bias " + str(i) + ": " + str(len(f)))

    if len(f) < lowestLines:
        lowestLines = len(f)
        bestBias = i

print("Best bias is " + str(bestBias) + " at " + str(lowestLines) + " steps")
colour_bias = bestBias

pre_defined_colours = {
    "blank": (0, 0, 0, []),
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

print("Building pixels...")
build_pixels()
print("Building sqeuence...")
build_sequence()

print("Done")
