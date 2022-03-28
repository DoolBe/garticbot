#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import mouse
import keyboard
import time
from PIL import Image,ImageGrab
from math import sqrt
from mouse import LEFT, DOWN, get_position, wait
from myani2sketch import ani2sketch
import pickle


MAINDIR ="./"
SLEEPCLICK, SLEEPMOVE = 0.01,0.00000001
stopDrawing = False
linemode = True

def GetPosition(positionname):
    print(positionname)
    mouse.wait(LEFT, mouse.DOWN)
    posi = get_position()
    print(posi)
    return posi

def Exit():
    global stopDrawing
    stopDrawing = True
    print("Exiting")


# In[ ]:


class Color:
    def __init__(self,name,r,g,b,mx,my,mz=-1):
        self.name = name
        self.R = r  
        self.G = g  
        self.B = b  
        self.RGB = (self.R,self.G,self.B)
        self.x = int(mx)  # also 1.0 index
        self.y = int(my)  # also 0.5 index
        self.z = int(mz)  # 0.5 white flag
        self.xy = (self.x,self.y)  
    def printData(self):
        print(f"{self.name}: {self.R},{self.G},{self.B}, X: {self.x} Y: {self.y}")

def getColorPanel(img,maxy,maxx,pLeftTop,pRightBottom):
    pix = img.load()
    xSize, ySize = img.size
    xOffset, yOffset = xSize/maxx, ySize/maxy
    x0,y0 = int(xOffset/2),int(yOffset/2)
    
    mxOffset = abs(pLeftTop[0]-pRightBottom[0])/maxx
    myOffset = abs(pRightBottom[1]-pLeftTop[1])/maxy
    mx0 = pLeftTop[0] + int(mxOffset/2)
    my0 = pLeftTop[1] + int(myOffset/2)
    
    panelColors = []
    blackIndex = 0
    whiteIndex = 1
    for x in range(maxx):
        for y in range(maxy):
            px, py = int(x0 + xOffset*x), int(y0 + yOffset*y)
            mx, my = int(mx0 + mxOffset*x),int(my0 + myOffset*y)
            r,g,b = pix[px,py][0],pix[px,py][1],pix[px,py][2]
            panelColors.append(Color("c"+str(x)+str(y),r,g,b,mx,my))
            
            if r<3 and g<3 and b<3:
                blackIndex = maxx*x+y
                print("Black is at "+str(blackIndex)+", "+str((x,y)))
            if r>250 and g>250 and b>250:
                whiteIndex = maxx*x+y
                print("white is at "+str(whiteIndex)+", "+str((x,y)))
    return panelColors,blackIndex,whiteIndex


# In[ ]:


def clickPen(posi):
    mouse.move(posi[0], posi[1], duration=0)
    time.sleep(SLEEPMOVE)
    mouse.click(LEFT)
    time.sleep(SLEEPCLICK)     
    
def getImageAndCanvas(relocate,testimg):
    if testimg:
        img = Image.open(MAINDIR+"testimg/"+str(testimg)+".jpg").convert('RGB')
    else:
        #input("ready")
        img = ImageGrab.grabclipboard().convert("RGB")
    if relocate:
        x0y0,xnyn = GetPosition("x0y0"),GetPosition("xnyn")
    else: 
        x0y0,xnyn = clefttop,crightbottom
    canvas = (abs(xnyn[0]-x0y0[0]),abs(xnyn[1]-x0y0[1]))
    if img:
        xSize, ySize = img.size
        ratio = min(canvas[0]/xSize, canvas[1]/ySize)
        img = img.resize((int(xSize*ratio),int(ySize*ratio)))
    else:  print("No Image.")
    return img,(min(xnyn[0],x0y0[0]),min(xnyn[1],x0y0[1]))

def getPixelSets(img,rgbDetail,skeDetail):    
    layer1colorsXYs = [[] for i in panelColors]
    layer2colorsXYs = [[] for i in panelColors]
    layer3colorsXYs = [[] for i in panelColors]
    rgbPixelSet = (layer1colorsXYs,layer2colorsXYs,layer3colorsXYs)
    sketchColorsXYs = [[]]
    
    if not img: return rgbPixelSet,sketchColorsXYs
    xSize, ySize = img.size
    if rgbDetail:pixRGB = img.load()
    if skeDetail:pixSKT = ani2sketch(img).load()
    
    for y in range(ySize): 
        for x in range(xSize):
            if rgbDetail and not x%rgbDetail and not y%rgbDetail:
                r,g,b = pixRGB[x, y]
                Index1,Index2,Index3 = colorXYZTable[r][g][b]
                if Index1 != whiteIndex:
                    rgbPixelSet[0][Index1].append((x,y))
                if Index2 != -1: 
                    rgbPixelSet[1][Index2].append((x,y))
                if Index3 != -1: 
                    rgbPixelSet[2][Index3].append((x,y))
            if skeDetail and not x%skeDetail and not y%skeDetail:
                r,g,b = pixSKT[x, y]
                if r<240 or g<240 or b<240: #skip white
                    sketchColorsXYs[0].append((x,y))
    return  rgbPixelSet,sketchColorsXYs

    
def drawSingleColor(colorXYs,x0y0,step):
    global linemode,stopDrawing
    if linemode:
        lastx,lasty,ishold = -1,-1,0
        for (x,y) in colorXYs:
            if(stopDrawing): 
                mouse.release()
                return True
            if x == lastx +step and y == lasty: 
                mouse.hold()
            else: 
                time.sleep(SLEEPCLICK)
                mouse.release()
                ishold=0
            mouse.move(x0y0[0]+x,x0y0[1]+y, duration=0)
            time.sleep(SLEEPMOVE)
            if not ishold:
                mouse.click()
                ishold = 1
            lastx,lasty = x, y
        time.sleep(SLEEPCLICK)
        mouse.release()
    else:
        for (x,y) in colorXYs:
            if(stopDrawing): return True
            clickPen((x0y0[0]+x,x0y0[1]+y))
    return False

def detail2pen(detail):
    if 0<=detail<3:
        return pen1
    elif 3<=detail<7:
        return pen2

def drawColor(testimg,relocate,rgbDetail,skeDetail):
    global stopDrawing    
    rgbpen = detail2pen(rgbDetail)
    skepen = detail2pen(skeDetail)
    img,x0y0 = getImageAndCanvas(relocate,testimg)
    
    rgbPixelSet,skePixelSet = getPixelSets(img,rgbDetail,skeDetail)
    layer1colorsXYs,layer2colorsXYs,layer3colorsXYs = rgbPixelSet
    sketchColorsXYs = skePixelSet
    
    if rgbDetail:
        stopDrawing = False
        clickPen(pen5)
        clickPen(rgbpen)
        # draw alpha 100
        clickPen(alpha100)
        for colorXYs in layer1colorsXYs:
            if(stopDrawing): continue
            clickPen(panelColors[layer1colorsXYs.index(colorXYs)].xy)
            stopDrawing = drawSingleColor(colorXYs,x0y0,rgbDetail)
        # draw alpha 50
        clickPen(alpha50)
        for colorXYs in layer2colorsXYs:
            if(stopDrawing): continue
            clickPen(panelColors[layer2colorsXYs.index(colorXYs)].xy)
            stopDrawing = drawSingleColor(colorXYs,x0y0,rgbDetail)
        # draw alpha 50 WHITE 3rd layer
        for colorXYs in layer3colorsXYs:
            if(stopDrawing): continue
            clickPen(panelColors[layer3colorsXYs.index(colorXYs)].xy)
            stopDrawing = drawSingleColor(colorXYs,x0y0,rgbDetail)
            
    if skeDetail:
        stopDrawing = False
        clickPen(pen5)
        clickPen(skepen)
        clickPen(alpha100)
        for colorXYs in sketchColorsXYs:
            if(stopDrawing): continue
            clickPen(panelColors[blackIndex].xy)
            stopDrawing = drawSingleColor(colorXYs,x0y0,skeDetail)


# In[ ]:


keyboard.add_hotkey("esc", Exit)
pLeftTop = GetPosition("mLeftTop")
pRightBottom = GetPosition("mRightBottom")
colorPanelImg = Image.open(MAINDIR+"weights/gartic-colors-source-6x3.jpg").convert('RGB')
panelColors,blackIndex,whiteIndex = getColorPanel(colorPanelImg,6,3,pLeftTop,pRightBottom)
file = open(MAINDIR+'weights/colorXY1Table.pypickle', 'rb')
colorXYZTable = pickle.load(file)
file.close()


# In[ ]:


alpha50 = GetPosition("alpha50")
alpha100 = GetPosition("alpha100")
pen1 = GetPosition("pen1")


# In[ ]:


clefttop= GetPosition("clefttop")
crightbottom = GetPosition("crightbottom")


# In[ ]:


pen5 = GetPosition("pen5")
pen2 = GetPosition("pen2")


# In[ ]:


drawColor(testimg=0,relocate=False,rgbDetail=5,skeDetail=2)


# In[ ]:


drawColor(testimg=0,relocate=True,rgbDetail=5,skeDetail=0)


# In[ ]:


drawColor(testimg=0,relocate=False,rgbDetail=0,skeDetail=2)


# In[ ]:


drawColor(testimg=0,relocate=True,rgbDetail=0,skeDetail=2)

