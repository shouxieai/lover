import cv2
import numpy as np

images = [cv2.imread(f"imgs/{i:05d}.jpg") for i in range(70)]

d = True
while True:
    if d:
        it = range(0, len(images))
    else:
        it = range(len(images)-1, -1, -1)

    d = not d
    for i in it:
        cv2.imshow("image", images[i])
        cv2.waitKey(3)

