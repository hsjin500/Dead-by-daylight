import cv2
import numpy as np
# import matplotlib.pyplot as plt
# plt.style.use('dark_background')  # plt 테마만 바꾸는것
from mss import mss
# 클자 인식
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
# 컴퓨터 조작
import win32com.client as comclt
import keyboard
import time, pyautogui
# from PIL import ImageGrab
###################################################################################
angle0 = -89
angle1 = 90
x0,y0,w0,h0,x1,y1,w1,h1 = 0,0,0,0,0,0,0,0
gauge_box = {'top': 464, 'left': 888, 'width': 146, 'height': 151}
# Center : 961.5 , 539
sct = mss()

while True:
    sct_img = sct.grab(gauge_box)
    img_np = np.array(sct_img)
    cv2.imshow('gauge_box', img_np) # 기본 이미지 인식 영역 확인
    ################################################ 이미지 BGR 데이터 hsv 로 변환, 범위내 색깔 추출
    #####0 : 흰영역
    hsv0 = cv2.cvtColor(img_np, cv2.COLOR_BGR2HSV)
#     cv2.imshow('aaa',hsv0)
    white_lo = np.array([0,0,168])
    white_hi = np.array([172,111,255])
    mask0 = cv2.inRange(hsv0, white_lo, white_hi)
    #####1 : 빨간bar
    hsv1 = cv2.cvtColor(img_np, cv2.COLOR_BGR2HSV)
    red_lo = np.array([0,180,180])
    red_hi = np.array([10,255,255])
    mask1 = cv2.inRange(hsv1, red_lo, red_hi)
    ################################################ 색 필터링 처리
    #####0
    kernel0 = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    opening0 = cv2.morphologyEx(mask0, cv2.MORPH_OPEN, kernel0, iterations=1)
    close0 = cv2.morphologyEx(opening0, cv2.MORPH_CLOSE, kernel0, iterations=1)
    #####1
    kernel1 = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    opening1 = cv2.morphologyEx(mask1, cv2.MORPH_OPEN, kernel1, iterations=1)
    close1 = cv2.morphologyEx(opening1, cv2.MORPH_CLOSE, kernel1, iterations=1)
    ################################################ 처리된 이미지 바탕으로 영역 추출 및 그리기
    #####0
    cnts0 = cv2.findContours(close0, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts0 = cnts0[0] if len(cnts0) == 2 else cnts0[1]
#     if len(cnts0) != 0 :
#         print(len(cnts0))
    offset = 0
    # Center : 73 , 75.5
    for c in cnts0:
        x0,y0,w0,h0 = cv2.boundingRect(c)
        cv2.rectangle(img_np, (x0, y0), (x0 + w0, y0 + h0), (255,0,0), 2)
        #---for문 안에 새로운 조건, 게이지가 떴을 때 영역이 1개만 나오게 하는 것은 이미 앞에서 색으로 분류함.
        #그 1개의 영역의 중심점과 전체 이미지 중심(원 중심) 사이의 거리를 구하자(나중에 각도를 구하려고)
        if len(cnts0) == 1 and ((x0+w0/2)-73) != 0 :
            angle0 = np.degrees(np.arctan((75.5-(y0+h0/2))/((x0+w0/2)-73)))
    #####1
    cnts1 = cv2.findContours(close1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts1 = cnts1[0] if len(cnts1) == 2 else cnts1[1]
#     offset = 0
    # Center : 71.5 , 70
    for c in cnts1:
        x1,y1,w1,h1 = cv2.boundingRect(c) # 아래로 갈수록 y 커짐, 오른쪽으로 갈수록 x 커짐.
        cv2.line(img_np, (73, 75),(73, 75), (36,255,12), 1)  # 중앙 점!
#         cv2.rectangle(img_np, (x - offset, y - offset), (x + w + offset, y + h + offset), (255,0,0), 2)
        if (x1-73)*(y1-75.5) > 0 : # 2,4 사분면 (오른쪽 아래가 2사분면 이지만 x,y양수)
            cv2.line(img_np, (x1,y1),(x1+w1-3, y1+h1-3), (36,255,12), 2)
        elif (x1-73) == 0 : # 선이 위, 아래 방향일 때
            cv2.line(img_np, (x1,y1),(x1, y1+h1-3), (36,255,12), 2)
        elif (y1-75.5) == 0 :  # 선이 좌, 우 방향일 때
            cv2.line(img_np, (x1,y1),(x1+w1-3, y1), (36,255,12), 2)
        else : # 1,3 사분면
            cv2.line(img_np, (x1,y1+h1),(x1+w1-3, y1-3), (36,255,12), 2)
        #---for문 안에 새로운 조건, 게이지가 떴을 때 영역이 1개만 나오게 하는 것은 이미 앞에서 색으로 분류함.
        #그 1개의 영역의 중심점과 전체 이미지 중심(원 중심) 사이의 거리를 구하자(나중에 각도를 구하려고)
        if len(cnts1) == 1 and ((x1+w1/2)-73) != 0:
            angle1 = np.degrees(np.arctan((75.5-(y1+h1/2))/((x1+w1/2)-73)))
    #################### 인게임 내에 Space 자동 동작 버튼 ######################
    # x는 정확하게 중심으로 안해도 된다. (X축 기준으로 각도를 구하기 때문에)
    if (angle0 - 8) <= angle1 <= (angle0 + 8) \
    and (x0-73)*(x1-73) > 0 \
    and (75.5-(y0+h0/2))*(75.5-(y1+h1/2)) != 0 :
        wsh= comclt.Dispatch("WScript.Shell")
        wsh.AppActivate("DeadByDaylight") # 앱 선택
        pyautogui.hotkey('space')
        print("space 작동!")
        print(f"흰 영역 : {angle0}")
        print(f"빨간 선 : {angle1}")
############################################################################
    cv2.imshow('mask0', mask0)
    cv2.imshow('mask', mask1)
    cv2.imshow('close0', close0)
    cv2.imshow('close', close1)
    cv2.imshow('image', img_np)
    if len(cnts0) == 0 :
        angle0 = - 89
    angle1 = 90
    if (cv2.waitKey(1) & 0xFF) == ord('q'):
#         text = pytesseract.image_to_string(img_np, lang='eng')
#         print(text)
        cv2.destroyAllWindows()  # cv2 창 종료
        break # 루프 종료
