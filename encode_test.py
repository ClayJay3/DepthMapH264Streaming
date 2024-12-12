import numpy as np
import cv2
import subprocess

# Image dimensions
width = 1280
height = 720

# 16-bit depth value
depth = 20000  # Example value, you can change this

# Normalize the depth value
w = 65536  # Maximum value for 16-bit
normalizedDepth = (depth + 0.5) / w

# Period for triangle waves
np_value = 512.0  # Example value, you can change this
p = np_value / w

# Linear mapping for low-resolution depth
L = normalizedDepth

# Triangle wave function 1
Ha = (L / (p / 2.0)) % 2.0
Ha = Ha if Ha <= 1.0 else 2.0 - Ha

# Triangle wave function 2 (phase-shifted by π/4)
Hb = ((L - (p / 4.0)) / (p / 2.0)) % 2.0
Hb = Hb if Hb <= 1.0 else 2.0 - Hb

# Create YUV420P image
Y = np.full((height, width), L * 255, dtype=np.uint8)
U = np.full((height // 2, width // 2), Ha * 255, dtype=np.uint8)
V = np.full((height // 2, width // 2), Hb * 255, dtype=np.uint8)

# Combine Y, U, V channels into a single YUV420P image
yuv_image = np.concatenate((Y.flatten(), U.flatten(), V.flatten()))

# Save the YUV image to a file
with open('image.yuv', 'wb') as f:
    f.write(yuv_image)

# Use ffmpeg to encode the YUV image to H264
subprocess.run([
    'ffmpeg', 
    '-s', f'{width}x{height}', 
    '-pix_fmt', 'yuv420p', 
    '-i', 'image.yuv', 
    '-c:v', 'libx264', 
    '-f', 'h264', 
    'output.h264'
])