import numpy as np
import cv2
import subprocess

# Constants
w = 65536.0
np_value = 512.0

# Decode the .h264 file to a YUV image
subprocess.run([
    'ffmpeg', 
    '-i', 'output.h264', 
    '-pix_fmt', 'yuv420p', 
    '-s', '1280x720', 
    'decoded_image.yuv'
])

# Read the YUV image
width = 1280
height = 720
with open('decoded_image.yuv', 'rb') as f:
    yuv_data = f.read()

# Extract Y, U, V channels
Y = np.frombuffer(yuv_data[0:width*height], dtype=np.uint8).reshape((height, width))
U = np.frombuffer(yuv_data[width*height:width*height + (width//2)*(height//2)], dtype=np.uint8).reshape((height//2, width//2))
V = np.frombuffer(yuv_data[width*height + (width//2)*(height//2):], dtype=np.uint8).reshape((height//2, width//2))

# Upsample U and V to match Y dimensions
U = cv2.resize(U, (width, height), interpolation=cv2.INTER_LINEAR)
V = cv2.resize(V, (width, height), interpolation=cv2.INTER_LINEAR)

# Create an empty matrix to store the decoded depth values
cvDecodedDepth = np.zeros((height, width), dtype=np.uint16)

# Iterate over each pixel in the YUV image
for y in range(height):
    for x in range(width):
        # Extract the encoded depth values
        L = Y[y, x] / 255.0
        Ha = U[y, x] / 255.0
        Hb = V[y, x] / 255.0

        # Period for triangle waves
        p = np_value / w

        # Determine offset and fine-grain correction
        m = int((4.0 * (L / p)) - 0.5) % 4
        L0 = L - ((L - (p / 8.0)) % p) + ((p / 4.0) * m) - (p / 8.0)

        if m == 0:
            delta = (p / 2.0) * Ha
        elif m == 1:
            delta = (p / 2.0) * Hb
        elif m == 2:
            delta = (p / 2.0) * (1.0 - Ha)
        elif m == 3:
            delta = (p / 2.0) * (1.0 - Hb)

        # Combine to compute the original depth
        depth = w * (L0 + delta)

        # Store the decoded depth in the new matrix
        cvDecodedDepth[y, x] = int(depth)

# Save the decoded depth image
cv2.imwrite('decoded_depth.png', cvDecodedDepth)

# Print the center pixel depth
center_y = height // 2
center_x = width // 2
center_pixel_depth = cvDecodedDepth[center_y, center_x]
print(f'Center pixel depth: {center_pixel_depth}')