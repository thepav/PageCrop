import cv2
import cv
import numpy as np
from math import *
def line_intersection(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1]) #Typo was here

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
       return None

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return x, y

def getLines(path):
    img_big = cv2.imread(path)
    height,width = img_big.shape[:2]
    print width,height
    img = img_big
    if height>width:
        if height>600 and width>400:
            img = cv2.resize(img_big, (300,400))
    else:
        if height>400 and width>600:
            img = cv2.resize(img_big, (400,300))

    height,width = img.shape[:2]

    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray,50,150,apertureSize = 3)

    foundLines = cv2.HoughLines(edges,1,np.pi/180,50)
    print foundLines
    count = 0
    thetas = []
    lines = []

    for rho,theta in foundLines[0]:
        if count==4:
            break
        countLine = True
        if len(thetas)==0:
            countLine= True
        else:
            sameThetaCount = 0
            for r,t in thetas:
                print str(fabs(t-theta)) + ',' + str(fabs(rho-r))

                if (fabs(t-theta) < 1.2 or fabs(t-theta) >1.9) and fabs(rho-r)<100:
                    countLine = False

                if fabs(t-theta) < 1.2 or fabs(t-theta) >1.9:
                    sameThetaCount+=1

                if sameThetaCount >1:
                    countLine = False

        if countLine:
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a*rho
            y0 = b*rho
            x1 = int(x0 + 1000*(-b))
            y1 = int(y0 + 1000*(a))
            x2 = int(x0 - 1000*(-b))
            y2 = int(y0 - 1000*(a))

            cv2.line(img,(x1,y1),(x2,y2),(0,0,255),2)
            count+=1
            thetas.append((rho,theta))
            lines.append(((x1,y1),(x2,y2)))

    if count <4:
        cv2.imwrite('lines.jpg',img)
        return None
    else:
        intersections = set([])
        for A,B in lines:
            for C,D in lines:
                if A != C and B != D:
                    intersection = line_intersection((A,B),(C,D))
                    if intersection and intersection[0]>0 and intersection[0]<width and intersection[1]>0 and intersection[1]<height:
                        intersections.add(intersection)

        for i in intersections:
            cv2.circle(img, i, 5, (0,0,255), -1)

        cv2.imwrite('lines.jpg',img)
        return intersections
def perspectiveCrop(path, corners):
    img = cv2.imread(path)
    cols,rows = img.shape[:2]
    corners.sort()

    pointsArray = []
    for tuples in corners:
        pointsArray.append([tuples[0],tuples[1]])

    pts1 = np.float32(pointsArray)
    pts2 = None
    relPointsArray = []
    if pointsArray[0][1]<pointsArray[1][1]:
        relPointsArray.append([0,0])
        relPointsArray.append([0,cols])
    else:
        relPointsArray.append([0,cols])
        relPointsArray.append([0,0])

    if pointsArray[2][1]<pointsArray[3][1]:
        relPointsArray.append([rows,0])
        relPointsArray.append([rows,cols])
    else:
        relPointsArray.append([rows,cols])
        relPointsArray.append([rows,0])

    pts2 = np.float32(relPointsArray)
    M = cv2.getPerspectiveTransform(pts1,pts2)

    dst = cv2.warpPerspective(img,M,(rows,cols))
    cv2.imwrite('crop.jpg',dst)


setOfCorners = getLines('receipt_7.jpg')
perspectiveCrop('receipt_7.jpg',list(setOfCorners))