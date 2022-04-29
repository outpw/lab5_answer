'''*********************************************
Author: Phil White
Date: 3/23/22
A solution to lab 5. Note: this script uses iterations and 
indexing to perform moving window analysis. Reasonable run time. 
This script was designed for comprehension by beginner programmers. 
See other solutions for faster methods. 
*********************************************'''

import time
ti = time.time()
import arcpy
import numpy as np
from arcpy import env
from arcpy import sa

print 'import time:',time.time()-ti
ti = time.time()

def circle_masker(winShape, radius):

    mask = np.zeros(winShape)
    for i in range(0,np.size(mask,1)):
        for j in range(0,np.size(mask,0)):
            if ((int(radius)-j)**2+(int(radius)-i)**2)**.5 <= radius:
                mask[j][i] = 1 
    return mask

def bool_maker(a,classes):
    
    boolOut = np.zeros(a.shape)
    for c in classes:
        boolOut += np.where(a==c,1,0)
    return boolOut

def perc_getter(boolArray,mask,thresholds,aType):
    
    outArray = np.zeros(boolArray.shape)
    
    if aType == 'rectangle':
        for i in range(4,np.size(nlcdArray,1)-4):
            for j in range(5,np.size(nlcdArray,0)-5):
                perc = (((boolArray[j-5:j+6,i-4:i+5] * mask).sum())/mask.sum())*100 
                if thresholds[0]<= perc <thresholds[1]:
                    outArray[j][i] = 1
                else:
                    outArray[j][i] = 0
    
    if aType == 'circle':
        for i in range(7,np.size(boolArray,1)-7):
            for j in range(7,np.size(boolArray,0)-7):
                perc = (((boolArray[j-7:j+8,i-7:i+8] * mask).sum())/mask.sum())*100 
                if thresholds[0]<= perc <thresholds[1]:
                    outArray[j][i] = 1
                else:
                    outArray[j][i] = 0
    #print outArray.sum()
    return outArray

def slope_analyzer(slopeArray,mask,threshold,aType):
    outArray = np.zeros(slopeArray.shape)
    if aType =='rectangle':
        for i in range(4,np.size(slopeArray,1)-4):
            for j in range(5,np.size(slopeArray,0)-5):
                if (np.sum(slopeArray[j-5:j+6,i-4:i+5] * mask)/mask.sum()) < threshold:
                    outArray[j][i] = 1
                else:
                    outArray[j][i] = 0
    
    if aType =='circle':
        for i in range(7,np.size(slopeArray,1)-7):
            for j in range(7,np.size(slopeArray,0)-7):
                if (np.sum(slopeArray[j-7:j+8,i-7:i+8] * mask)/mask.sum()) < threshold:
                    outArray[j][i] = 1
                else:
                    outArray[j][i] = 0
    return outArray

ti = time.time()

arcpy.CheckOutExtension('SPATIAL')

env.workspace = r'C:\Users\phwh9568\GEOG_4303\Lab5\data\results'
env.overwriteOutput = 1

slopeRaster = sa.Slope(r'C:\Users\phwh9568\GEOG_4303\Lab5\data\dem_lab5')
cellSize = slopeRaster.meanCellWidth
crs = slopeRaster.spatialReference
llpt = slopeRaster.extent.lowerLeft
slopeArray = arcpy.RasterToNumPyArray(slopeRaster)
nlcdArray = arcpy.RasterToNumPyArray(r'C:\Users\phwh9568\GEOG_4303\Lab5\data\nlcd06_lab5')
shape = nlcdArray.shape

#classes
greenClasses = [41,42,43,52]
agClasses = [81,82]
liDevClasses = [21,22]
waterClasses = [11]
classList = [greenClasses,agClasses,liDevClasses,waterClasses]

#thresholds
greenThresh = (30,101)
agThresh = (0,5)
liDevThresh = (0,20)
waterThresh = (5,20)
thresholds = [greenThresh,agThresh,liDevThresh,waterThresh]

analysisType = 'rectangle'
if analysisType == 'circle':
    winShape = 15,15
    radius = (((float(11)/2)**2) + ((float(9)/2)**2))**.5
    mask = circle_masker(winShape,radius)
elif analysisType == 'rectangle':
    winShape = 11,9
    mask = np.ones((winShape))

bools = [bool_maker(nlcdArray,classes) for classes in classList]

outArrays = [perc_getter(bools[i],mask,thresholds[i],analysisType) for i in range(len(bools))]

slope8Array = slope_analyzer(slopeArray,mask,8,analysisType)
model = np.zeros(shape)

for out in outArrays:
    model += out

model = model + slope8Array
hiDev = np.where(nlcdArray==23,0,1) * np.where(nlcdArray==24,0,1)
outModel = model * hiDev

outRaster = arcpy.NumPyArrayToRaster(outModel.astype(int),llpt,cellSize,cellSize)
arcpy.management.DefineProjection(outRaster,crs)
outRaster.save('suite_suitability.tif')

print 'total suitable pixels:',np.where(outModel==5,1,0).sum()
print time.time() - ti