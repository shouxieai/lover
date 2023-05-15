import cv2
import numpy as np


width = 1024
height = 680

image = np.zeros((height, width, 3), np.uint8)


def interpolation(a, b, t):
    return a * (1 - t) + b * t

def bezier(points, t):
    if len(points) == 1: return points[0]

    points = np.stack(points)
    interp_points = []
    for i in range(0, len(points)-1):
        interp_points.append(interpolation(points[i], points[i+1], t))
    return bezier(np.stack(interp_points), t)

def rend_points(image, points, ts=100):

    if len(points) > 0:
        for t in np.linspace(0, 1, ts):
            p = bezier(points, t)
            cv2.circle(image, (int(p[0]), int(p[1])), 1, (0, 255, 0), -1, 16)

            fx = 2 * points[0][0]- p[0]
            cv2.circle(image, (int(fx), int(p[1])), 1, (0, 255, 0), -1, 16)

        for i, (x, y) in enumerate(points):
            color = (0, 0, 255)
            if i == 0 or i == len(points) - 1:
                color = (200, 200, 200)
            cv2.circle(image, (int(x), int(y)), 3, color, -1, 16)

def find_drop_point(points, x, y):
    pts = np.stack(points, axis=0)
    dist = np.linalg.norm(pts - [x, y], axis=1)
    min_idx = dist.argmin()
    min_dist = dist[min_idx]
    if min_dist < 20:
        return min_idx
    return -1

def make_callback(points):
    drop_point = -1
    key_down   = False
    def callback(event, x, y, flags, user):
        nonlocal drop_point, key_down
        if event == cv2.EVENT_LBUTTONDOWN:
            if flags & cv2.EVENT_FLAG_ALTKEY:
                drop_point = find_drop_point(points, x, y)
                key_down = drop_point != -1
            else:
                if len(points) >= 2:
                    points.insert(len(points)-1, [x, y])
                else:
                    points.append([x, y])
        elif event == cv2.EVENT_MOUSEMOVE:
            if key_down:
                if drop_point == 0 or drop_point == len(points) - 1:
                    points[drop_point][1] = y
                else:
                    points[drop_point] = x, y
        elif event == cv2.EVENT_LBUTTONUP:
            key_down = False
            drop_point = -1
            print(points)
    return callback

points = [
    [width / 2, height * 0.3],
    [width / 2, height * 0.8],
]
# points = [[512.0, 204.0], (421, 9), (99, 209), (376, 358), (495, 493), [512.0, 544.0]]
name   = "bezier"
cv2.namedWindow(name)
cv2.resizeWindow(name, width, height)
cv2.setMouseCallback(name, make_callback(points))

while True:
    image[:] = 0
    rend_points(image, points)
    cv2.imshow(name, image)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break