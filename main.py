import cv2
import time
import numpy as np
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import math
import HandTrackingModule as htm

wCam, hCam = 648, 488

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

pTime = 0
detector = htm.handDetector(0.7)
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPer = 0
circle_color = (255,0,255)
line_color = (34,57,159)

def findvolume(volume):
    return int(volume)

while True:
    succ, img = cap.read()
    img = cv2.flip(img, 1)  # vertically flip
    img = detector.findHands(img)
    lmList = detector.findPosition(img,draw=False)
    if len(lmList[0]) != 0:
        lmList = lmList[0]
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        cv2.circle(img, (x1, y1), 10, (255, 0, 0), cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (255, 0, 0), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 1)
        cv2.circle(img, (cx, cy), 10, (255, 0, 0), cv2.FILLED)

        length = math.hypot(x2 - x1, y2 - y1)
        # print(length)

        # Hand range 50 - 300
        # Volume Range -65 - 0

        vol = np.interp(length, [50, 300], [minVol, maxVol])
        volBar = np.interp(length, [50, 300], [400, 150])
        volPer = np.interp(length, [50, 300], [0, 100])
        print(int(length), vol)
        maxlen = 170
        revol = -((maxlen-length)/maxlen)*96
        try:
            volume.SetMasterVolumeLevel(revol, None)
        except:
            pass

        dispvol = int((length/240)*100)
        cv2.putText(img, f'volume {dispvol}', (40, 110), cv2.FONT_HERSHEY_COMPLEX,
                    0.6, (255, 0, 0), 2)

        cv2.putText(img, f'{dispvol}', (cx,cy), cv2.FONT_HERSHEY_COMPLEX,
                    1, (0, 0, 255), 3)

        if length < 50:
            cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)


    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, f'FPS {int(fps)}', (40, 70), cv2.FONT_HERSHEY_COMPLEX,
                1, (255, 0, 0), 3)

    cv2.imshow("Img", img)

    if cv2.waitKey(30) & 0xFF == ord('q'):
        break
