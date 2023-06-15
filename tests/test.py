import cv2
import numpy as np
import json

## can be changed to read all images in a folder
img = cv2.imread("pikrex-crop-tool/tests/sousounofrieren_vol1_c1_page3.png")
img_height, img_width, c = img.shape

f = open('pikrex-crop-tool/tests/sousounofrieren_vol1_c1_page3_crops.json')
all_crops = json.load(f)
all_crops_cleaned = []

canvas_width = all_crops[0]['cwidth']
canvas_height = all_crops[0]['cheight']

for crop in all_crops[1:]:
    points_cleaned = []
    for point in crop['points']:
        ## scaling 
        ## in the cropping app, the image scales to the canvas width, affecting the points
        ## hence we need to scale the points back to the correct image size
        point_x = round(point['x']/canvas_width*img_width) if point['x'] > 0 else 0
        point_y = round(point['y']/canvas_height*img_height) if point['y'] > 0 else 0
        points_cleaned.append([point_x, point_y])
    all_crops_cleaned.append(points_cleaned)

for i in range(len(all_crops_cleaned)):
    pts = np.array(all_crops_cleaned[i])

    ## (1) Crop the bounding rect
    x,y,w,h = cv2.boundingRect(pts)
    print(x,y,w,h)
    cropped = img[y:y+h, x:x+w].copy()

    ## (2) make mask
    pts = pts - pts.min(axis=0)
    mask = np.zeros(cropped.shape[:2], np.uint8)
    cv2.drawContours(mask, [pts], -1, (255, 255, 255), -1, cv2.LINE_AA)

    ## (3) add alpha channel for transparent cropping
    new_img = cv2.cvtColor(cropped, cv2.COLOR_BGR2BGRA)
    new_img[:, :, 3] = mask

    ## (4) do bit-op
    dst = cv2.bitwise_and(new_img, new_img, mask=mask)

    cv2.imwrite("pikrex-crop-tool/tests/crop"+str(i)+".png", dst)