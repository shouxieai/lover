import imageio

frames = [
    imageio.imread(f"imgs/{i:05d}.jpg") for i in range(0, 70, 2)
]
frames = frames + frames[::-1]
print(len(frames))
imageio.mimsave('./lover.gif', # output gif
                frames,          # array of input frames
                format='GIF', fps=60)         # optional: frames per second