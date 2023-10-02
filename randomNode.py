# randomNode.py
#   Produces random locations to be used with the Maya instancer node.

import sys
import random
import os
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds
import maya.mel as mel

from LSystemInstanceNode import LSystemInstanceNode, LSystemInstanceNodeInitializer, LSystemInstanceNodeCreator

# Useful functions for declaring attributes as inputs or outputs.
def MAKE_INPUT(attr):
    attr.setKeyable(True)
    attr.setStorable(True)
    attr.setReadable(True)
    attr.setWritable(True)
def MAKE_OUTPUT(attr):
    attr.setKeyable(False)
    attr.setStorable(False)
    attr.setReadable(True)
    attr.setWritable(False)

# Give the node a unique ID. Make sure this ID is different from all of your
# other nodes!
randomNodeId = OpenMaya.MTypeId(0x8701)
LSystemInstanceNodeId = OpenMaya.MTypeId(0x8204)

# Node definition
class randomNode(OpenMayaMPx.MPxNode):
    # Declare class variables:
    # DONE:: declare the input and output class variables
    #         i.e. inNumPoints = OpenMaya.MObject()

    inNumPoints = OpenMaya.MObject()
    inMinX = OpenMaya.MObject()
    inMinY = OpenMaya.MObject()
    inMinZ = OpenMaya.MObject()
    inMinv = OpenMaya.MObject()

    inMaxX = OpenMaya.MObject()
    inMaxY = OpenMaya.MObject()
    inMaxZ = OpenMaya.MObject()
    inMaxv = OpenMaya.MObject()

    outPoints = OpenMaya.MObject()


    # constructor
    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)

    # compute
    def compute(self,plug,data):
         # TODO:: create the main functionality of the node. Your node should
        #         take in three floats for max position (X,Y,Z), three floats
        #         for min position (X,Y,Z), and the number of random points to
        #         be generated. Your node should output an MFnArrayAttrsData
        #         object containing the random points. Consult the homework
        #         sheet for how to deal with creating the MFnArrayAttrsData.

        if plug == randomNode.outPoints:
            # get values from inputs
            inNumPointsData = data.inputValue(self.inNumPoints)
            inNumPointsValue = inNumPointsData.asInt()
            minVecData = data.inputValue(self.inMinv)
            minVecData = minVecData.asFloat3()

            maxVecData = data.inputValue(self.inMaxv)
            maxVecData = maxVecData.asFloat3()

            outputData = data.outputValue(self.outPoints)

            arrAttrsData = OpenMaya.MFnArrayAttrsData()
            arrAttrsDataObject = arrAttrsData.create()

            arrPos = arrAttrsData.vectorArray("position")
            arrId = arrAttrsData.doubleArray("id")

            # fill MFnArrayAttrsData with random positions
            for i in range(0, inNumPointsValue):
                x = random.uniform(minVecData[0], maxVecData[0]);
                y = random.uniform(minVecData[1], maxVecData[1]);
                z = random.uniform(minVecData[2], maxVecData[2]);

                arrPos.append(OpenMaya.MVector(x,y,z))
                arrId.append(i)
            # output the MFnArrayAttrsData
            outputData.setMObject(arrAttrsDataObject)

        data.setClean(plug)
    
def randomNodeInitializer():
    tAttr = OpenMaya.MFnTypedAttribute()
    nAttr = OpenMaya.MFnNumericAttribute()

    # DONE:: initialize the input and output attributes. Be sure to use the 
    #         MAKE_INPUT and MAKE_OUTPUT functions.
    randomNode.inNumPoints = nAttr.create("numpoints", "np", OpenMaya.MFnNumericData.kInt, 10)
    MAKE_INPUT(nAttr)
    randomNode.inMinX = nAttr.create("minX", "lx", OpenMaya.MFnNumericData.kFloat, 0.0)
    MAKE_INPUT(nAttr)
    randomNode.inMinY = nAttr.create("minY", "ly", OpenMaya.MFnNumericData.kFloat, 5.0)
    MAKE_INPUT(nAttr)
    randomNode.inMinZ = nAttr.create("minZ", "lz", OpenMaya.MFnNumericData.kFloat, 0.0)
    MAKE_INPUT(nAttr)
    randomNode.inMaxX = nAttr.create("maxX", "rx", OpenMaya.MFnNumericData.kFloat, 5.0)
    MAKE_INPUT(nAttr)
    randomNode.inMaxY = nAttr.create("maxY", "ry", OpenMaya.MFnNumericData.kFloat, 0.0)
    MAKE_INPUT(nAttr)
    randomNode.inMaxZ = nAttr.create("maxZ", "rz", OpenMaya.MFnNumericData.kFloat, 5.0)
    MAKE_INPUT(nAttr)
    randomNode.inMinv = nAttr.create("minv", "lv", randomNode.inMinX, randomNode.inMinY, randomNode.inMinZ)
    MAKE_INPUT(nAttr)
    randomNode.inMaxv = nAttr.create("maxv", "rv", randomNode.inMaxX, randomNode.inMaxY, randomNode.inMaxZ)
    MAKE_INPUT(nAttr)
    randomNode.outPoints = tAttr.create("outPoints", "op", OpenMaya.MFnArrayAttrsData.kDynArrayAttrs)
    MAKE_OUTPUT(tAttr)

    try:
        randomNode.addAttribute(randomNode.inNumPoints)
        randomNode.addAttribute(randomNode.inMinv)
        randomNode.addAttribute(randomNode.inMaxv)
        randomNode.addAttribute(randomNode.outPoints)

        randomNode.attributeAffects(randomNode.inNumPoints, randomNode.outPoints)
        randomNode.attributeAffects(randomNode.inMinv, randomNode.outPoints)
        randomNode.attributeAffects(randomNode.inMaxv, randomNode.outPoints)

    except:
         sys.stderr.write( ("Failed to create attributes of %s node\n", randomNodeId) )

# creator
def randomNodeCreator():
    return OpenMayaMPx.asMPxPtr( randomNode() )

# initialize the script plug-in
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.registerNode( "randomNode", randomNodeId, randomNodeCreator, randomNodeInitializer )
        mplugin.registerNode( "LSystemInstanceNode", LSystemInstanceNodeId, LSystemInstanceNodeCreator, LSystemInstanceNodeInitializer)
    except:
         sys.stderr.write( "Failed to register %s node\n" % randomNodeId)
    LSystemInstanceNode.path = str(mplugin.loadPath())
    melPath = LSystemInstanceNode.path + "/LSystemNode.mel"
    mel.eval("source \"{}\";".format(str(melPath)))

# uninitialize the script plug-in
def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode( randomNodeId )
        mplugin.deregisterNode( LSystemInstanceNodeId )
    except:
        sys.stderr.write( "Failed to unregister %s node\n" % randomNodeId )