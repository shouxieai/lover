import cv2
import numpy as np

def interpolation(a, b, t):
    return a * (1 - t) + b * t

def bezier(points, t):
    if len(points) == 1: return points[0]

    points = np.stack(points)
    interp_points = []
    for i in range(0, len(points)-1):
        interp_points.append(interpolation(points[i], points[i+1], t))
    return bezier(np.stack(interp_points), t)

def make_points(points, ts=150):
    new_points = []
    for t in np.linspace(0, 1, ts):
        p = bezier(points, t)
        new_points.append(p)

        fx = 2 * points[0][0]- p[0]
        new_points.append([fx, p[1]])
    return np.stack(new_points)

width = 1024
height = 680
center = np.array([width, height]).reshape(-1, 2) / 2
state0 = np.array([[512.0, 204.0], (421, 9), (99, 209), (376, 358), (495, 493), [512.0, 544.0]]) - [1024/2, 680/2]
state1 = np.array([[512.0, 146], (420, -18), (82, 202), (292, 363), (362, 524), [512.0, 566]]) - [1024/2, 680/2]
state0 *= 1
state1 *= 1
stateN = make_points(state0 * 0.01)
stateN2 = make_points(state0 * 0.35)
stateB = make_points(state1 * 1.1)
state0 = make_points(state0)
state1 = make_points(state1)

# https://cubic-bezier.com/
weights = []
for t in np.linspace(0, 1, 70):
    weights.append(bezier(np.array([
        [0, 0],
        [.0,.82],
        [0.14,0.99],
        [1, 1]
    ]), t)[1])
weights = (1-np.stack(weights))[::-1]

color_a = np.array([176, 98, 255])
color_b = np.array([255, 198, 255])
color_ca = np.array([176, 98, 255])
color_cb = np.array([255, 198, 255])
image = np.zeros((height, width, 3), np.uint8)

for i, t in enumerate(weights):
    image[:] = 0
    np.random.seed(3)
    current = interpolation(state0, state1, t)
    particles = []
    for rc in np.linspace(1, 0.0, 200):
        nkeep = max(3, int(rc ** 8 * len(stateN)))
        idx_keep = np.random.choice(np.arange(len(stateN)), size=nkeep)
        for sn, sn2, s0, sc in zip(stateN[idx_keep], stateN2[idx_keep], state0[idx_keep], current[idx_keep]):
            # p = interpolation(interpolation(s0, s1, rc) + (np.random.rand() * 2 - 1) * 30 * (1 - rc), s1, weights[t])
            p0 = interpolation(sn, sc, rc) + (np.random.rand(2) * 2 - 1) * 30 * (1 - rc*0.90)
            p1 = interpolation(sn2, sc, rc)
            p = interpolation(p0, p1, t * min(1.0, rc / 0.05))
            particles.append(p)

    particles = np.stack(particles, axis=0)
    particles = ((particles + center) * 16).astype(np.int32)
    for x, y in particles:
        size = int(np.random.rand() * 3 * 16)
        color = interpolation(color_a, color_b, np.random.rand())
        cv2.circle(image, (x, y), size, color, -1, 16, shift=4)

    np.random.seed(i // 5)
    for rc in np.linspace(1, 0.0, 150):
        nkeep = int(np.random.rand() * rc * len(stateN))
        idx_keep = np.random.choice(np.arange(len(stateN)), size=nkeep)
        for sn, sb in zip(stateN[idx_keep], state1[idx_keep]):
            # p = interpolation(sn, sb, (np.random.rand() + (1 - t) * 0.2) * (0.8 + t*0.2)) + (np.random.rand() * 2 - 1) * 30 * (1 - rc*0.90)
            a = (np.random.randn() * 0.8) * (1 - t) * 0.1 + 0.9
            p = interpolation(sn, sb, a * rc * (0.9 + (1-t) * 0.15)) + (
                        np.random.rand(2) * 2 - 1) * 30
            x, y = ((p + center[0]) * 16).astype(np.int32)
            size = int(np.random.rand() * 1 * 16)
            color = interpolation(color_ca, color_cb, np.random.rand())
            cv2.circle(image, (x, y), size, color, -1, 16, shift=4)

    cv2.imshow("image", image)
    cv2.imwrite(f"imgs/{i:05d}.jpg", image)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break