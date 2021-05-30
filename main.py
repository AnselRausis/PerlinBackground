import numpy as np
import random
import math
import cv2 as cv
from perlin_noise import PerlinNoise
import time
import ctypes
import os
import pathlib
import imageio

"""
Design choices:
-Save images in files:
    Reason I did this was because if the user wanted to save as gif, it could be constructed using the images.
    Also, they can select which version of the image they wanted as permanent stable background.
    Animation time can be changed by changing the sleep under display_files function, though I found it stops working lower than .2
    I had no idea why the above happens but *shrug*.

Issues:
There is a delay between the end of one animation and the start another.
A possible fix could be threading.... but idk rn
"""

# Paths
absolute_path = str(pathlib.Path().absolute())
path_to_frames = r"" + absolute_path + "\\frames"
gif_file_name = r"" + absolute_path + "\\PerlinFractal.gif"
imagepath = r"" + absolute_path + "\\PerlinFractal.jpg"

if not os.path.exists(path_to_frames):
    os. mkdir(path_to_frames)

# users stuff
user32 = ctypes.windll.user32
dimensions = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]


# Display forwards and backwards
def display(list_of_files):
    display_files(list_of_files)
    backwards_files = reversed(list_of_files)
    display_files(backwards_files)

def display_singular(filename):

    ctypes.windll.user32.SystemParametersInfoW(20, 0, f"" + filename, 0)

"""
Display based on list of files inputted
"""


def display_files(list_of_files):
    for file in list_of_files:
        ctypes.windll.user32.SystemParametersInfoW(20, 0, f"" + file, 0)
        time.sleep(.55)


# Init files for adding to frames
def image_init(filename, img):
    try:
     os.remove(filename)
    except Exception:
        print("File Deletion Issue")
    cv.imwrite(filename, img)


def save_image_to_frames(image, num_frame, currentpath):
    save_path = currentpath + "\\" + str(num_frame) + ".png"
    image_init(save_path, image)
    return save_path

def getcolor():

    color = []
    hue = random.randint(0, 1)

    color.append(random.randint(0, 255))

    if hue == 0:
        color.append(random.randint(0, 255))

    i = len(color) - 1

    if random.randint(0,2) == 1:
        if color[i] < 125:
            color.append(random.randint(color[i]+50, 175))
        else:
            color.append(random.randint(25, color[i] - 50))
    else:
        if color[i] > 75:
            color.append(random.randint(25, color[i] - 50))
        else:
            color.append(random.randint(color[i] + 50, 175))

    if hue == 1:
        color.append(random.randint(0, 255))

    return color


# No idea what most of this does but it works   <<It's magic
def create_images(size, zoom, animated, colorvariation, delay):
    images = []

    # Sets dimensions to the screen's aspect ratio
    w = size[0]
    h = size[1]

    # Creates a numpy empty pixel array, essentially a blank canvas
    frame = np.zeros((math.ceil(h * 2 / zoom), math.ceil(w * 2 / zoom), 3), np.uint8)

    # Uses some math to adjust bounds of the shape accordingly to the screen
    middle = [math.ceil(w / zoom), math.ceil(h / zoom)]
    r = math.sqrt(pow(w / 2, 2) + pow(h / 2, 2))
    dotsize = math.ceil(r / 10)

    # Creates the main form of variation for the shape, by generating Perlin noise in a random octave range
    variation = random.randint(20, 35)
    noise = PerlinNoise(octaves=variation, seed=random.randint(1, 10000))

    # Sets up some numbers later used for angle variation
    axistilt = random.randint(0, 90)
    offset = random.randint(0, 270)

    # Trying to create a more dynamic color sytam than entierly random, as to have less bad colors
    colors = []
    colors.append(getcolor())
    colors.append(getcolor())
    colorincriment = 180/colorvariation

    for i in range(0, 180):

        # Selects a different color every few frames, slowly shifts between them for all other frames

        if i % (math.ceil(colorincriment)) == 0:
            colors.pop(0)
            colors.append(getcolor())
            deltacolor = [math.ceil((colors[1][0] - colors[0][0]) / colorincriment), math.ceil((colors[1][1] - colors[0][1]) / colorincriment),
                          math.ceil((colors[1][2] - colors[0][2]) / colorincriment)]
            color = colors[0]

        # Uses some perlin noise to generate a radius

        if abs(noise(1 / (i * 2 + 1))) < 1 / 3:
            currentradius = abs(noise(1 / (i + 1)) * r * 3)
        else:
            currentradius = r

        # Selects angle offsets for both the shapes and mirror axis to add variation

        deltatheta = axistilt - ((2 * i) % 90)
        axisangle = math.floor((2 * i) / 90) + axistilt

        # Magic

        for j in range(0, 4):

            sign1 = (j % 2) * 2 - 1
            sign2 = math.floor(j / 2)

            xdif = math.ceil(
                currentradius * math.cos((axisangle + (deltatheta * sign1) + (180 * sign2) + offset) * math.pi / 180))
            ydif = math.ceil(
                currentradius * math.sin((axisangle + (deltatheta * sign1) + (180 * sign2) + offset) * math.pi / 180))

            try:
                cv.circle(frame, (middle[0] + xdif, middle[1] + ydif),
                          math.floor(dotsize * 75 / variation * abs(noise(1 / (i + 1)))), (color[0], color[1], color[2]), -1)
            except:
                print("Out of bounds")

        # Vertical mirroring of magic

        for j in range(0, 4):

            sign1 = (j % 2) * 2 - 1
            sign2 = math.floor(j / 2) * 2 - 1

            xdif = math.ceil(
                currentradius * math.cos((axisangle + (deltatheta * sign1) + (90 * sign2) + offset) * math.pi / 180))
            ydif = math.ceil(
                currentradius * math.sin((axisangle + (deltatheta * sign1) + (90 * sign2) + offset) * math.pi / 180))

            try:
                cv.circle(frame, (middle[0] + xdif, middle[1] + ydif),
                          math.floor(dotsize * 75 / variation * abs(noise(1 / (i + 1)))),
                          (color[0], color[1], color[2]), -1)
            except:
                print("Out of bounds")

            #Color iteration

            for num, col in enumerate(color):
                color[num] += deltacolor[num]


        # Adds image to file and adds it to list
        if animated and i % 3 == 0:
            images.append(save_image_to_frames(frame, i, path_to_frames))
            display_singular(images[len(images)-1])
            time.sleep(0.25)
    if animated:
        time.sleep(delay)
        for index in range(0, len(images)):
            display_singular(images[len(images) - index - 1])
            time.sleep(0.35)
    else:
        try:
            os.remove(imagepath)
        except:
            print("fileNotFound")
        cv.imwrite(imagepath, frame)

        ctypes.windll.user32.SystemParametersInfoW(20, 0, imagepath, 0)
        time.sleep(delay)





"""
This is designed for creating a gif so someone can save the whole gif if they wanted
"""


def create_gif_from_image():
    images = []
    file_names = create_images(dimensions, .5)
    for file in file_names:
        images.append(imageio.imread(file))
    imageio.mimsave(gif_file_name, images, fps=20)

Animate = True
timedelay = 5
totalcolors = 5

while True:

    if Animate:
        files = create_images(dimensions, .5, Animate, totalcolors, timedelay)
        # print("Displaying New Files")
        # display(files)
    else:
        image = create_images(dimensions, .5, Animate, totalcolors, timedelay)
        try:
            os.remove(imagepath)
        except:
            print("fileNotFound")
        cv.imwrite(imagepath, image)

        ctypes.windll.user32.SystemParametersInfoW(20, 0, imagepath, 0)
        time.sleep(timedelay)

