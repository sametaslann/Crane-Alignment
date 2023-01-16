from asyncore import write
import math
from unicodedata import numeric
import cv2 as cv
import numpy as np
import time


cap = cv.VideoCapture(0,cv.CAP_DSHOW)

radius = 0 #asdkmaskdlsa
realRadius = 3 #1 metredeki gerçek circle çapı 

ret,frame = cap.read()

#Set the frame size
frame = cv.resize(frame,(1920,1080))
cap.set(cv.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)

height = frame.shape[0]
width = frame.shape[1]

print(frame.shape)
while True:
    ret,frame = cap.read()

    if frame is None:
        break
    
    originalFrame = frame.copy()
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

    #Range of Red color in HSV colorspace
    lower_red = np.array([160,100,20])
    upper_red = np.array([179,255,255])

    #Masking and bitwise processes
    red_mask = cv.inRange(hsv,lower_red,upper_red)
    red_color = cv.bitwise_and(frame, frame, mask= red_mask)


    #Blurring and Finding circles
    gray = cv.cvtColor(red_color, cv.COLOR_BGR2GRAY)
    gray_blurred = cv.GaussianBlur(gray, (7,7), cv.BORDER_DEFAULT)
    
    # https://pyimagesearch.com/2014/07/21/detecting-circles-images-using-opencv-hough-circles/
    # Parameters has been explained in this website
    circles = cv.HoughCircles(gray_blurred, cv.HOUGH_GRADIENT, 1,200,param1=50,
                              param2=30,minRadius=0,maxRadius=100)
    # param1 and2 -> Threshold of sensitive for detecting circles

    # Draw rectangle to the middle of the frame as much as radius of circle
    cv.rectangle(originalFrame, ((width//2)-radius, (height//2)-radius), ((width//2)+radius, (height//2)+radius), (0, 0, 255), thickness=1)

    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        
        #Handle the properties of circle 
        for (circ_x,circ_y,circ_r) in circles:
            
            radius = circ_r
            
            #6.83 -> 1cmlik dairenin 100 cm uzaklığındaki pixel sayısı [1920,1080]
            horizontalDist = 100*6.83*realRadius/radius
            
            #Distance from the center of the camera to the center of the circe in PIXELS 
            verticalPx = math.sqrt(abs((width//2)-circ_x)*abs((width//2)-circ_x) + abs((height//2)-circ_y)*abs((height//2)-circ_y))
            print(verticalPx)

            # 100 -> reference distance
            #6.83 reference pixel of circle        
            #I don't know where '2' comes from :::)            
            verticalDistance = (horizontalDist) / (100*6.83*2) * (verticalPx)
            
            #Finds degree by using some math rules             
            degree = (180/math.pi)*np.arctan(verticalDistance/horizontalDist)
            degree = round(degree,2)
            
            
            centerOfCamera = (width//2, height//2)
            centerOfCircle = (circ_x, circ_y)
            blueColor = (255, 0, 0)
            CyanColor = (255,255,0)
            
            
            #Print some variables to the frame as text
            finalStr = "Deg:" + str(degree) +str(round(horizontalDist,1)) + "-r:" + str(radius) + "-Vh:" + str(verticalDistance) + "-Ho: " + str(horizontalDist)
            cv.putText(originalFrame, str(finalStr), (30,30), cv.FONT_HERSHEY_SIMPLEX, 1, blueColor, thickness=2)
            
            
            #Draws line from center of the camera to center of the circle
            cv.line(img=originalFrame, pt1 = centerOfCamera, pt2=centerOfCircle, color=blueColor, thickness=3, lineType=5, shift=0)
            
            ## If the red circle area is within the borders of the rectangular area, Draw the circles 
            if circ_x < width//2+radius and circ_x > width//2-radius and circ_y >  height//2-radius and circ_y <  height//2+radius:
                print("Coordinates: " , circles)
                cv.circle(originalFrame, (circ_x,circ_y) ,circ_r , CyanColor,2)
                cv.circle(originalFrame, (circ_x,circ_y) ,1 , CyanColor,3)
           

    cv.imshow("Circle", originalFrame)        

    k = cv.waitKey(5) & 0xFF 

    if k == ord('q'):
        break