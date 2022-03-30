
'''
from PIL import ImageCms
import numpy as np
def rgb2lab(img):
    srgb_p = ImageCms.createProfile("sRGB")
    lab_p  = ImageCms.createProfile("LAB")
    rgb2lab = ImageCms.buildTransformFromOpenProfiles(srgb_p, lab_p, "RGB", "LAB")
    return ImageCms.applyTransform(img, rgb2lab)
    

def FindClosestColor(rgb: tuple, targetColors):
    allColors = targetColors
    values = list()
    for color in allColors:
        dr = rgb[0] - color.RGB[0]
        dg = rgb[1] - color.RGB[1]
        db = rgb[2] - color.RGB[2]
        rr = (rgb[0] + color.RGB[0])/2
        
        #diff = sqrt(dr*dr+dg*dg+db*db)
        diff = sqrt((2+rr/256)*dr*dr +4*dg*dg+(2+(255-rr)/256)*db*db)
        values.append(diff)
    index_min = min(range(len(values)), key=values.__getitem__)
    return index_min
    
def getMixedColor(panelColors):
    mixColors = []
    panelColorTypes = len(panelColors)
    for x in range(panelColorTypes):
        for y in range(panelColorTypes):
            if y<x: continue
            if x==y: # same color, set y=-1 to skip alpha50
                mixColors.append(Color("m"+str(x)+str(y),
                                       panelColors[x].R,panelColors[x].G,panelColors[x].B,
                                       x,-1))
                continue
            fullColor = panelColors[x]
            halfColor = panelColors[y]
            mixr = int((fullColor.R + halfColor.R)/2)
            mixg = int((fullColor.G + halfColor.G)/2)
            mixb = int((fullColor.B + halfColor.B)/2)
            mixColors.append(Color("m"+str(x)+str(y),mixr,mixg,mixb,x,y))
    return mixColors

def getMixedWhiteColor(panelColors,whiteIndex,mixColors):
    mixWhiteColors = []
    for i in range(len(mixColors)):
        z = whiteIndex
        fullColor = mixColors[i]
        x,y = fullColor.xy
        halfColor = panelColors[z]
        mixr = int((fullColor.R + halfColor.R)/2)
        mixg = int((fullColor.G + halfColor.G)/2)
        mixb = int((fullColor.B + halfColor.B)/2)
        if y>=0:  #
            mixWhiteColors.append(Color("mw"+str(x)+str(y)+str(1),mixr,mixg,mixb,x,y,z))
        mixWhiteColors.append(Color("mw"+str(x)+str(y)+str(0),fullColor.R,fullColor.G,fullColor.B,x,y,-1))
    return mixWhiteColors


def getMixed3Color(panelColors,mixColors):
    mix3Colors = []
    mixColorTypes = len(mixColors)
    panelColorTypes = len(panelColors)
    for i in range(mixColorTypes):
        for z in range(panelColorTypes):
            fullColor = mixColors[i]
            x,y = fullColor.xy
            halfColor = panelColors[z]
            mixr = int((fullColor.R + halfColor.R)/2)
            mixg = int((fullColor.G + halfColor.G)/2)
            mixb = int((fullColor.B + halfColor.B)/2)
            if y==-1 and z==x:  #
                mix3Colors.append(Color("mm"+str(x)+str(y)+str(z),fullColor.R,fullColor.G,fullColor.B,x,y,-1))
                continue
            mix3Colors.append(Color("mm"+str(x)+str(y)+str(z),mixr,mixg,mixb,x,y,z))
    return mix3Colors
    

mixedColors = getMixedColor(panelColors)
mixWhiteColors = getMixedWhiteColor(panelColors,whiteIndex,mixedColors)
mix3Colors = getMixed3Color(panelColors,mixedColors)

colorXY1Table = [[[(-1,-1,-1) for b in range(256)] for g in range(256)] for r in range(256)]
for r in range(256):
    for g in range(256):
        for b in range(256):
            mixedIndex = FindClosestColor((r,g,b),mixWhiteColors)
            color100,color50 = mixWhiteColors[mixedIndex].xy
            isWhite50 = mixWhiteColors[mixedIndex].z
            colorXY1Table[r][g][b] = (color100,color50,isWhite50)
            
            
            
colorXYZTable = [[[(-1,-1,-1) for b in range(256)] for g in range(256)] for r in range(256)]
for r in range(256):
    for g in range(256):
        for b in range(256):
            mixedIndex = FindClosestColor((r,g,b),mix3Colors)
            color100,color50 = mix3Colors[mixedIndex].xy
            isWhite50 = mix3Colors[mixedIndex].z
            colorXYZTable[r][g][b] = (color100,color50,isWhite50)
            

file = open(MAINDIR+'weights/colorXYZTable.pypickle', 'wb')
pickle.dump(colorXYZTable, file)
file.close()
'''


'''
def getPixelSets(img,rgbDetail,skeDetail):  
    xSize, ySize = img.size    
    rgbPixelSet=([],[],[])
    sketchColorsXYs = []
    if rgbDetail:
        rgbxy = (xSize//rgbDetail,ySize//rgbDetail)
        pixRGB = img.resize(rgbxy).load()
        layer1colorsXYs = [[[0 for y in range(rgbxy[1])] for x in range(rgbxy[0])] for i in panelColors]
        layer2colorsXYs = [[[0 for y in range(rgbxy[1])] for x in range(rgbxy[0])] for i in panelColors]
        layer3colorsXYs = [[[0 for y in range(rgbxy[1])] for x in range(rgbxy[0])] for i in panelColors]
        rgbPixelSet = (layer1colorsXYs,layer2colorsXYs,layer3colorsXYs)
        for y in range(rgbxy[1]): 
            for x in range(rgbxy[0]):
                r,g,b = pixRGB[x, y]
                Index1,Index2,Index3 = colorXYZTable[r][g][b]
                if Index1 != whiteIndex:
                    rgbPixelSet[0][Index1][x][y]=1
                if Index2 != -1: 
                    rgbPixelSet[1][Index2][x][y]=1
                if Index3 != -1: 
                    rgbPixelSet[2][Index3][x][y]=1        
    if skeDetail:
        skexy = (xSize//skeDetail,ySize//skeDetail)
        pixSKT = ani2sketch(img.resize(skexy)).load() 
        sketchColorsXYs = [[[0 for y in range(skexy[1])] for x in range(skexy[0])]]
        for y in range(skexy[1]): 
            for x in range(skexy[0]):
                r,g,b = pixSKT[x, y]
                if r<240 or g<240 or b<240: #skip white
                    sketchColorsXYs[0][x][y]=1
    return  rgbPixelSet,sketchColorsXYs

def drawSingleColor(isColorXYs,x0y0,step):
    global linemode,stopDrawing
    colorXYs = drawOrder(isColorXYs)
    if linemode:
        lastx,lasty,ishold = -1,-1,0
        for (x,y) in colorXYs:
            if(stopDrawing): 
                mouse.release()
                return True
            if abs(x-lastx) <=1 and abs(y-lasty) <=1: 
                mouse.hold()
            else: 
                time.sleep(SLEEPCLICK)
                mouse.release()
                ishold=0
            mouse.move(x0y0[0]+step*x,x0y0[1]+step*y, duration=0)
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
            clickPen((x0y0[0]+step*x,x0y0[1]+step*y))
    return False
'''