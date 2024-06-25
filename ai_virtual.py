import cv2
import numpy as np
import HandTrackingModule as htm
import time
import pyautogui
import logging

##########################
wCam, hCam = 320, 240  # Reduce the camera resolution to improve performance
frameR = 100  # Frame Reduction
smoothening = 7
clickThreshold = 30  # Adjust this threshold based on your requirements
clickConfirmTime = 0.3  # Time in seconds to confirm a click
#########################

pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0
clickStartTime = 0

# Set up logging
logging.basicConfig(filename='click_accuracy.log', level=logging.INFO, format='%(asctime)s:%(message)s')

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
detector = htm.handDetector(maxHands=1)
wScr, hScr = pyautogui.size()

while True:
    # 1. Find hand Landmarks
    success, img = cap.read()
    if not success:
        continue

    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img, draw=False)  # Disable drawing to improve performance

    # 2. Get the tip of the index and middle fingers
    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]
        x0, y0 = lmList[4][1:]  # Thumb tip

    # 3. Check which fingers are up
    fingers = detector.fingersUp() if len(lmList) != 0 else []

    # Draw a rectangle on the screen
    cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)

    # 4. Only Index Finger : Moving Mode
    if len(fingers) != 0 and fingers[1] == 1 and fingers[2] == 0:
        # 5. Convert Coordinates
        x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
        y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))

        # 6. Smoothen Values
        clocX = plocX + (x3 - plocX) / smoothening
        clocY = plocY + (y3 - plocY) / smoothening

        # 7. Move Mouse
        pyautogui.moveTo(wScr - clocX, clocY)
        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        plocX, plocY = clocX, clocY

    # 8. Both Index and middle fingers are up : Clicking Mode
    if len(fingers) != 0 and fingers[1] == 1 and fingers[2] == 1:
        # 9. Find distance between fingers
        length, img, lineInfo = detector.findDistance(8, 12, img, draw=False)  # Disable drawing to improve performance
        # print(length)
        # 10. Click mouse if distance short
        if length < clickThreshold:
            if clickStartTime == 0:
                clickStartTime = time.time()
            elif time.time() - clickStartTime > clickConfirmTime:
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                pyautogui.click()
                logging.info('Click detected')
                clickStartTime = 0  # Reset click start time after a click
        else:
            clickStartTime = 0  # Reset click start time if distance is not maintained

    # 11. Thumb and Index fingers are up: Zooming Mode (Zoom In)
    if len(fingers) != 0 and fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
        print("Zooming In")
        pyautogui.hotkey('ctrl', '+')

    # 12. Middle and Ring fingers are up: Zooming Mode (Zoom Out)
    if len(fingers) != 0 and fingers[0] == 0 and fingers[3] == 1 and fingers[1] == 0 and fingers[2] == 1 and fingers[4] == 0:
        print("Zooming Out")
        pyautogui.hotkey('ctrl', '-')

    # 13. Frame Rate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

    # 14. Display
    cv2.imshow("Image", img)
    cv2.waitKey(1)
