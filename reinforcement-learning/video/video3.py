import cv2
import os


def make_video():
    # windows:
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    # Linux:
    fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
    out = cv2.VideoWriter('/Users/sebastian/Repos/MLTest/reinforcement-learning/video/qlearn.avi', fourcc, 60.0, (1200, 900))

    for i in range(0, 2350, 10):
        img_path = f"/Users/sebastian/Repos/MLTest/reinforcement-learning/video/qtable_charts/{i}.png"
        print(img_path)
        frame = cv2.imread(img_path)
        out.write(frame)

    out.release()


make_video()