from PIL import Image
import os
import cv2
import math
import statistics
import json
import numpy as np

class node:
    def __init__(self, cost, cons) -> None:
        self.dist = 999999999999999999999999
        self.cost = cost
        self.connections = cons
        self.pathTo = []
    def cpy (self):
        return (node(self.cost, self.connections[:]))

t = os.path.dirname(__file__)
def filepath (path):
    return (os.path.join(t, path))

def mapImage (img):
    w = img.width
    h = img.height
    x = 0
    y = 0

    map = []

    x = 0
    y = 0
    while x < h:
        map.append([])
        y = 0      
        while y < w:
            map[x].append (img.getpixel((y, x)))
            y+=1
        x+=1

    return (map)

def getEnergy (imgLst, ignore):
    returnVar = []
    h = len(imgLst)
    w = len(imgLst[0]) - ignore
    for i, row in enumerate(imgLst):
        returnVar.append([])
        for j, px in enumerate (row):
            if (j > w-1):
                break
            xs = []
            ys = []
            if i == 0:
                xs.append (imgLst[h-1][j])
            else:
                xs.append (imgLst[i-1][j])

            if j == 0:
                ys.append (imgLst[i][w-1])
            else:
                ys.append (imgLst[i][j-1])

            if i == h-1:
                xs.append (imgLst[0][j])
            else:
                xs.append (imgLst[i+1][j])

            if j == w-1:
                ys.append (imgLst[i][0])
            else:
                ys.append (imgLst[i][j+1])

            returnVar[i].append (((getGradient(xs)+getGradient(ys))**0.5)/10)
    return returnVar
            
def getGradient (pixels):
    returnVar = 0
    for i, color in enumerate(pixels[0]):
        cur = 0
        cur = pixels[0][i] - pixels[1][i]
        returnVar+= cur**2
    return returnVar

def imgToNode (pixels):
    returnVar = []
    for n in range(len(pixels)):
        returnVar.append ([])
    i = len(pixels) - 1
    while True:
        row = pixels[i]
        for j, px in enumerate (row):
            if i == len(pixels) - 1:
                returnVar[i].append (node(px, []))
            else:
                if (len(pixels[0]) == 1):
                    returnVar[i].append (node(px, [returnVar[i+1][j]]))
                elif j == 0:
                    returnVar[i].append (node(px, [None, returnVar[i+1][j], returnVar[i+1][j+1]]))
                elif j == len(row) - 1:
                    returnVar[i].append (node(px, [returnVar[i+1][j-1], returnVar[i+1][j], None]))
                else:
                    returnVar[i].append (node(px, [returnVar[i+1][j-1], returnVar[i+1][j], returnVar[i+1][j+1]]))

        i -= 1
        if i == -1:
            break
    return returnVar


def findPaths (nodes):
    for i, row in enumerate(nodes):
        for j, element in enumerate (row):
            if i == 0:
                element.pathTo = [j]
                element.dist = element.cost
            for n, dest in enumerate (element.connections):
                if dest == None:
                    continue
                if (dest.dist > element.dist+dest.cost):
                    dest.dist = element.dist+dest.cost
                    dest.pathTo = element.pathTo[:]
                    dest.pathTo.append (j+n-1)

def markSeam (img, bestSeam):
    for i, row in enumerate(img):
        row[bestSeam[i]] = (255,0,0,255)


def deleteSeam (img, bestSeam):
    for i, row in enumerate(img):
        row.pop(bestSeam[i])
        row.append ([0,255,0,255])

if __name__== "__main__" :
    im = mapImage (Image.open(filepath ("target.png")))
    video=cv2.VideoWriter(filepath('myvideo.mp4'),cv2.VideoWriter_fourcc(*'mp4v'), 15,(len(im[0]),len(im)))
    frames = 0
    while True:
        print (str(frames) + "/" + str(len(im[0])))
        if frames == len(im[0]):
            break

        gradiented = getEnergy(im, frames)
        
        
        #gradientedImg = np.array(gradiented, dtype=np.uint8)
        #gradientedImg = Image.fromarray(gradientedImg)
        #gradientedImg.save(filepath("gradient.png"))
        
        gradNodes = imgToNode (gradiented)
        findPaths (gradNodes)
        bestSeam = []
        bestVal = 999999999999999999999999999
        for end in gradNodes[-1]:
            if end.dist < bestVal:
                bestSeam = end.pathTo[:]
                bestVal = end.dist
        
        markSeam (im, bestSeam)
        img = np.array(im, dtype=np.uint8)
        img = Image.fromarray(img)

        video.write(np.array(img.convert('RGB'))[:, :, ::-1].copy())
        deleteSeam (im, bestSeam)
        frames += 1

    print ("done")
    video.release()