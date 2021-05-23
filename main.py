import numpy as np
import random
import math
import cv2 as cv
from perlin_noise import PerlinNoise
import time
import ctypes
import os
import pathlib

filename = 'PerlinFractal.jpg'
temp_path = str(pathlib.Path().absolute()) + "\\" + filename
path = r"" + temp_path

user32 = ctypes.windll.user32
dimensions = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]

def display(img):

    try:
        os.remove(filename)
    except:
        print("File not Found")
    cv.imwrite(filename, img)

    ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 0)


def scribble(size, zoom):

    w = size[0]
    h = size[1]

    frame = np.zeros((math.ceil(h * 2 / zoom), math.ceil(w * 2 / zoom), 3), np.uint8)

    middle = [math.ceil(w / zoom), math.ceil(h / zoom)]

    r = math.sqrt(pow(w / 2, 2) + pow(h / 2, 2))

    dotsize = math.ceil(r / 10)

    variation = random.randint(10, 40)

    offset = random.randint(0, 270)
    noise = PerlinNoise(octaves=variation, seed=random.randint(1, 10000))

    axistilt = random.randint(0, 90)

    color = []
    shade1 = random.randint(70, 255)
    color.append(shade1)


    if random.randint(0, 2) == 1:
        color.append(random.randint(0, 255))
        color.append(0)
        red = False
    else:
        color.append(0)
        color.append(random.randint(0, 255))
        red = True


    for i in range(0, 180):

        color[0] += random.randint(-20, 20)
        if red:
            color[2] += random.randint(-20, 20)
        else:
            color[1] += random.randint(-20, 20)

        if abs(noise(1 / (i * 2+1))) < 1/3:
            currentradius = abs(noise(1 / (i+1)) * r * 3)
        else:
            currentradius = r

        deltatheta = axistilt - ((2 * i)%90)
        axisangle = math.floor((2 * i)/90) + axistilt

        for j in range(0, 4):

            sign1 = (j % 2) * 2 - 1
            sign2 = math.floor(j / 2)

            xdif = math.ceil(currentradius * math.cos((axisangle + (deltatheta * sign1) + (180 * sign2) + offset) * math.pi / 180))
            ydif = math.ceil(currentradius * math.sin((axisangle + (deltatheta * sign1) + (180 * sign2) + offset) * math.pi / 180))

            try:
                cv.circle(frame, (middle[0] + xdif, middle[1] + ydif), math.floor(dotsize * 2 * abs(noise(1 / (i + 1)))), (color[0], color[1], color[2]), -1)
            except:
                print("Out of bounds")

        for j in range(0, 4):

            sign1 = (j % 2) * 2 - 1
            sign2 = math.floor(j / 2) * 2 - 1

            xdif = math.ceil(currentradius * math.cos((axisangle + (deltatheta * sign1) + (90 * sign2) + offset) * math.pi / 180))
            ydif = math.ceil(currentradius * math.sin((axisangle + (deltatheta * sign1) + (90 * sign2) + offset) * math.pi / 180))

            try:
                cv.circle(frame, (middle[0] + xdif, middle[1] + ydif),
                      math.floor(dotsize * 75 / variation * abs(noise(1 / (i + 1)))), (color[0], color[1], color[2]), -1)
            except:
                print("Out of bounds")


    return frame

while True:

    current = scribble(dimensions, 0.5)
    display(current)

    time.sleep(1)
