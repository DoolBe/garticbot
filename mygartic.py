#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import mouse
import keyboard
import time
from PIL import Image,ImageCms,ImageGrab
from math import sqrt
from mouse import LEFT, DOWN, get_position, wait
import numpy as np

MAINDIR ="./"
RGBCOLOR = False
stopDrawing = False
SLEEPCLICK, SLEEPMOVE = 0.0001,0.00000001
PIXELDENSE = 2
allColors = []

class Color:
    def __init__(self,name,r,g,b,mx,my):
        self.name = name
        self.R = r  #L
        self.G = g  #A
        self.B = b  #B
        self.RGB = (self.R,self.G,self.B)
        self.x = int(mx)
        self.y = int(my)
        allColors.append(self)
    def printData(self):
        print(f"{self.name}: {self.R},{self.G},{self.B}, X: {self.x} Y: {self.y}")

def GetPosition(positionname):
    print(positionname)
    mouse.wait(LEFT, mouse.DOWN)
    posi = get_position()
    print(posi)
    return posi

def openImage(filename):
    #print(MAINDIR+filename)
    srgb_p = ImageCms.createProfile("sRGB")
    lab_p  = ImageCms.createProfile("LAB")
    rgb2lab = ImageCms.buildTransformFromOpenProfiles(srgb_p, lab_p, "RGB", "LAB")
    img = Image.open(MAINDIR+filename).convert('RGB')
    if RGBCOLOR: 
        return img
    else: 
        return ImageCms.applyTransform(img, rgb2lab)

def Exit():
    global stopDrawing
    stopDrawing = True
    print("Exiting")
    
def getColorPanel(colorfileName,maxy,maxx):
    img = openImage(colorfileName)
    pix = img.load()
    xSize, ySize = img.size
    xOffset, yOffset = xSize/maxx, ySize/maxy
    x0,y0 = int(xOffset/2),int(yOffset/2)
    
    mLeftTop = GetPosition("mLeftTop")
    mRightBottom = GetPosition("mRightBottom")
    mxOffset = abs(mLeftTop[0]-mRightBottom[0])/maxx
    myOffset = abs(mRightBottom[1]-mLeftTop[1])/maxy
    mx0 = mLeftTop[0] + int(mxOffset/2)
    my0 = mLeftTop[1] + int(myOffset/2)
    
    for x in range(maxx):
        for y in range(maxy):
            px, py = int(x0 + xOffset*x), int(y0 + yOffset*y)
            mx, my = int(mx0 + mxOffset*x),int(my0 + myOffset*y)
            color = Color("c"+str(x)+str(y),pix[px,py][0],pix[px,py][1],pix[px,py][2],mx,my)


# In[ ]:


def FindClosestColor(rgb: tuple):
    values = list()
    for color in allColors:
        dr = rgb[0] - color.RGB[0]
        dg = rgb[1] - color.RGB[1]
        db = rgb[2] - color.RGB[2]
        rr = (rgb[0] + color.RGB[0])/2
        
        #number = sqrt((2+rr/256)*dr*dr +4*dg*dg+(2+(255-rr)/256)*db*db)
        number = sqrt(dr*dr+dg*dg+db*db)
        #number = sqrt(dg*dg+db*db)+sqrt(dr*dr)
        #if color.name == "c10": number +=100
        values.append(number)
    index_min = min(range(len(values)), key=values.__getitem__)
    return index_min


# In[ ]:


def drawColor():
    global stopDrawing
    stopDrawing = False
    
    detailLevel=int(input("ready") or "3")
    img = ImageGrab.grabclipboard()
    clefttop= GetPosition("clefttop")
    crightbottom = GetPosition("crightbottom")
    time.sleep(0.5)
    
    if not img:
        print("No Image.")
        return
    xSize, ySize = img.size
    canvas = (crightbottom[0]-clefttop[0],crightbottom[1]-clefttop[1])
    pixelstep = min(canvas[0]/xSize/PIXELDENSE, canvas[1]/ySize/PIXELDENSE)
    if pixelstep<1:
        img = img.resize((int(xSize*pixelstep),int(ySize*pixelstep)))
        pixelstep = 1
    xSize, ySize = img.size
    
    srgb_p = ImageCms.createProfile("sRGB")
    lab_p  = ImageCms.createProfile("LAB")
    rgb2lab = ImageCms.buildTransformFromOpenProfiles(srgb_p, lab_p, "RGB", "LAB")
    if not RGBCOLOR: 
        img = ImageCms.applyTransform(img, rgb2lab)
    pix = img.load()
    
    lastcolor = 'Name'
    for y in range(int(ySize)):
        for x in range(int(xSize)):
            if(stopDrawing): return
            
            if x%detailLevel or y%detailLevel:continue
            colorIndex = FindClosestColor(pix[x, y])
            if colorIndex == 1: continue # colorIndex = 1 is white
            
            if lastcolor != allColors[colorIndex].name:
                colorPosition = (allColors[colorIndex].x, allColors[colorIndex].y)
                time.sleep(SLEEPMOVE)
                mouse.move(colorPosition[0], colorPosition[1], duration=0)
                time.sleep(SLEEPMOVE)
                mouse.click(LEFT)
                time.sleep(SLEEPCLICK)
                lastcolor = allColors[colorIndex].name
            
            mouse.move(clefttop[0]+int(x*pixelstep*PIXELDENSE),clefttop[1]+int(y*pixelstep*PIXELDENSE), duration=0)
            time.sleep(SLEEPMOVE)
            mouse.click(LEFT)
            time.sleep(SLEEPCLICK)


# In[ ]:


allColors = []
keyboard.add_hotkey("esc", Exit)
getColorPanel("gartic-colors-source-6x3.jpg",6,3)


# In[ ]:


SLEEPCLICK, SLEEPMOVE = 0.0001,0.00000001
PIXELDENSE = 1
#drawColor()
#drawLine()
#drawSingleColor()


# In[ ]:


while True:
    drawColor()


# In[ ]:





# In[ ]:


'''def drawSingleColor():
    global stopDrawing
    stopDrawing = False
    
    detailLevel=int(input("ready") or "3")
    img = ImageGrab.grabclipboard()
    clefttop= GetPosition("clefttop")
    crightbottom = GetPosition("crightbottom")
    time.sleep(1)
    
    xSize, ySize = img.size
    canvas = (crightbottom[0]-clefttop[0],crightbottom[1]-clefttop[1])
    pixelstep = min(canvas[0]/xSize/PIXELDENSE, canvas[1]/ySize/PIXELDENSE)
    if pixelstep<1:
        img = img.resize((int(xSize*pixelstep),int(ySize*pixelstep)))
        pixelstep = 1
    xSize, ySize = img.size
    
    srgb_p = ImageCms.createProfile("sRGB")
    lab_p  = ImageCms.createProfile("LAB")
    rgb2lab = ImageCms.buildTransformFromOpenProfiles(srgb_p, lab_p, "RGB", "LAB")
    if not RGBCOLOR: 
        img = ImageCms.applyTransform(img, rgb2lab)
    pix = img.load()
    
    colorSets = [[] for z in allColors]
    for x in range(int(xSize)):
        for y in range(int(ySize)):
            colorIndex = FindClosestColor(pix[x, y])
            colorSets[colorIndex].append((x,y))
            
    for colorxy in colorSets:
        
        currentIndex = colorSets.index(colorxy)
        colorPosition = (allColors[currentIndex].x, allColors[currentIndex].y)
        time.sleep(SLEEPCLICK)
        mouse.move(colorPosition[0], colorPosition[1], duration=0)
        time.sleep(SLEEPCLICK)
        mouse.click(LEFT)
        
        if(stopDrawing):return
        
        lastx,lasty = -1,-1
        for (x,y) in colorxy:
            
            if(stopDrawing):mouse.release();  return
            if x%detailLevel or y%detailLevel:continue
            
            if x == lastx and y == lasty+detailLevel: mouse.hold()
            else: mouse.release()
                
            mouse.move(clefttop[0]+x,clefttop[1]+y, duration=0)
            time.sleep(SLEEPCLICK)
            mouse.click()
            lastx,lasty = x, y'''


# In[ ]:


'''def drawLine():
    global stopDrawing
    stopDrawing = False
    
    detailLevel=int(input("ready") or "3")
    img = ImageGrab.grabclipboard()
    clefttop= GetPosition("clefttop")
    crightbottom = GetPosition("crightbottom")
    time.sleep(1)
    
    xSize, ySize = img.size
    canvas = (crightbottom[0]-clefttop[0],crightbottom[1]-clefttop[1])
    pixelstep = min(canvas[0]/xSize/PIXELDENSE, canvas[1]/ySize/PIXELDENSE)
    if pixelstep<1:
        img = img.resize((int(xSize*pixelstep),int(ySize*pixelstep)))
        pixelstep = 1
    xSize, ySize = img.size
    
    srgb_p = ImageCms.createProfile("sRGB")
    lab_p  = ImageCms.createProfile("LAB")
    rgb2lab = ImageCms.buildTransformFromOpenProfiles(srgb_p, lab_p, "RGB", "LAB")
    if not RGBCOLOR: 
        img = ImageCms.applyTransform(img, rgb2lab)
    pix = img.load()
    
    lastcolor = 'Name'
    mousehold = 0
    for y in range(int(ySize)):
        for x in range(int(xSize)):
            if(stopDrawing): return
            if x%detailLevel or y%detailLevel:continue
                
            colorIndex = FindClosestColor(pix[x, y])
            if lastcolor == allColors[colorIndex].name:
                mouse.hold()
            else:
                mouse.release()
                mousehold = 0
                time.sleep(SLEEPCLICK)
                if colorIndex == 1: continue # colorIndex = 1 is white
                    
                colorPosition = (allColors[colorIndex].x, allColors[colorIndex].y)
                time.sleep(SLEEPMOVE)
                mouse.move(colorPosition[0], colorPosition[1], duration=0)
                time.sleep(SLEEPMOVE)
                mouse.click(LEFT)
                time.sleep(SLEEPCLICK)
                lastcolor = allColors[colorIndex].name
            
            mouse.move(clefttop[0]+int(x*pixelstep*PIXELDENSE),clefttop[1]+int(y*pixelstep*PIXELDENSE), duration=0)
            time.sleep(SLEEPMOVE)
            if not mousehold:
                mouse.click()
                mousehold = 1
        mouse.release()
        mousehold = 0
        time.sleep(SLEEPCLICK)
'''

