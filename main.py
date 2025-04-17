import PIL.Image as Image


def calculate_required_moves(current_cursor, current_colour_cursor, current_rgb, target_pixel):
    # Calculates the number of moves needed to print the target pixel from the current cursors
    rgb = target_pixel[0]
    x = target_pixel[1]
    y = target_pixel[2]

    slider_moves = []
    cursor_moves = []

    # Adjust RGB sliders
    move_rgb_slider(current_colour_cursor, 0, current_rgb, rgb, slider_moves)
    move_rgb_slider(current_colour_cursor, 1, current_rgb, rgb, slider_moves)
    move_rgb_slider(current_colour_cursor, 2, current_rgb, rgb, slider_moves)

    # Move to target cursor
    target_cursor = (x, y)
    move_cursor(current_cursor, target_cursor, cursor_moves)

    return max(len(slider_moves), len(cursor_moves))


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
            # xyrgb = (a[1], a[2], a[0][0] * colour_bias, a[0][1] * colour_bias, a[0][2] * colour_bias)
            # currentXyrgb = (current[1], current[2], current[0][0] * colour_bias, current[0][1] * colour_bias,
            #                 current[0][2] * colour_bias)

            d = calculate_required_moves([current[1], current[2]], [3, 0, 0],
                                         [current[0][0], current[0][1], current[0][2]], a)
            if d < nearestDistance:
                nearest = a
                nearestDistance = d

        done.append(current)
        current = nearest
        remaining.remove(nearest)

        print(len(remaining))

    return done


all_pixels = []


def build_pixels():
    global all_pixels

    im = Image.open("in.png")
    im.thumbnail((62, 62), Image.Resampling.LANCZOS)
    out = Image.new("RGBA", (62, 62), 0xffffff)

    width, height = im.size
    for x in range(width):
        for y in range(height):
            r, g, b, a = im.getpixel((x, y))
            pixel = (r, g, b)

            if a == 0:
                continue

            all_pixels.append((pixel, x, y))

    x = 0
    y = 0

    all_pixels = sort_nearest_neighbour(all_pixels)

    for pixel in all_pixels:
        # print(pixel)
        toWrite = (pixel[0][0], pixel[0][1], pixel[0][2], 255)

        out.putpixel((pixel[1], pixel[2]), toWrite)
        x += 1
        if x == im.width:
            x = 0
            y += 1

    out.save("out.png")


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


# rgb param: 0 = red, 1 = green, 2 = blue
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


def build_sequence():
    out = open("out.txt", "w+", encoding="utf-8")

    pixels_remaining = len(all_pixels)
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

    cursor = [0, 0]
    # Index 0: 0 = red, 1 = green, 2 = blue, 3 = Pre-defined section
    colour_cursor = [3, 0, 0]

    # Move to first pixel
    pixel1 = all_pixels[0]
    x = pixel1[1]
    y = pixel1[2]

    target_cursor = (x, y)
    movements = []
    move_cursor(cursor, target_cursor, movements)
    for m in movements:
        out.write(m + "\n")

    current_rgb = [0, 0, 0]

    # Draw each pixel
    for pixel in all_pixels:
        rgb = pixel[0]
        x = pixel[1]
        y = pixel[2]

        slider_moves = []
        cursor_moves = []

        # Adjust RGB sliders
        move_rgb_slider(colour_cursor, 0, current_rgb, rgb, slider_moves)
        move_rgb_slider(colour_cursor, 1, current_rgb, rgb, slider_moves)
        move_rgb_slider(colour_cursor, 2, current_rgb, rgb, slider_moves)

        # Move to target cursor
        target_cursor = (x, y)
        move_cursor(cursor, target_cursor, cursor_moves)

        # Write
        k = 0
        for slider_move in slider_moves:
            if k < len(cursor_moves):
                out.write(slider_move + "," + cursor_moves[k] + "\n")
            else:
                out.write(slider_move + "\n")

            k += 1

        while k < len(cursor_moves):
            out.write(cursor_moves[k] + "\n")
            k += 1

        # Draw
        out.write("a\n")
        pixels_remaining -= 1

        out.write("-remaining: " + str(pixels_remaining) + "\n")

    out.close()


def decimal_range(start, stop, increment):
    while start < stop:
        yield start
        start += increment


print("Building pixels...")
build_pixels()
print("Building sequence...")
build_sequence()

print("Done")
