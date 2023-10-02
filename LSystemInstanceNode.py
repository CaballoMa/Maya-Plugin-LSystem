import sys
import os
import random
import LSystem
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds
import math

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

class AttrsData():
    def __init__(self):
        dataObj = OpenMaya.MFnArrayAttrsData()
        self.obj = dataObj.create()
        self.ids = dataObj.doubleArray("id")
        self.pos = dataObj.vectorArray("position")
        self.scales = dataObj.vectorArray("scale")
        self.aimDirs = dataObj.vectorArray("aimDirection")

class LSystemInstanceNode(OpenMayaMPx.MPxNode):
    angle = OpenMaya.MObject()
    step = OpenMaya.MObject()
    grammarFile = OpenMaya.MObject()
    iterations = OpenMaya.MObject()

    outBranches = OpenMaya.MObject()
    outFlowers = OpenMaya.MObject()
    path = ""

    # constructor
    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)

    # compute
    def compute(self,plug,data):
        def getInputs():
            angleVal = data.inputValue(LSystemInstanceNode.angle).asFloat()
            stepVal = data.inputValue(LSystemInstanceNode.step).asFloat()
            grammarFileVal = data.inputValue(LSystemInstanceNode.grammarFile).asString()
            iterationsVal = data.inputValue(LSystemInstanceNode.iterations).asInt()
            return angleVal, stepVal, grammarFileVal, iterationsVal
        
        angle, step, grammarFile, iters = getInputs()

        lsystem = LSystem.LSystem()
        lsystem.loadProgram(LSystemInstanceNode.path + '/' + grammarFile)
        print("Path: " + LSystemInstanceNode.path + '/' + grammarFile)
        lsystem.setDefaultAngle(angle)
        lsystem.setDefaultStep(step)
        branches = LSystem.VectorPyBranch()
        flowers = LSystem.VectorPyBranch()

        lsystem.processPy(iters, branches, flowers)

        outBranchData = AttrsData()
        outFlowerData = AttrsData()

        for i, branch in enumerate(branches):
            outBranchData.ids.append(i)
            begin = OpenMaya.MVector(branch[0], branch[2], branch[1])
            end = OpenMaya.MVector(branch[3], branch[5], branch[4])
            outBranchData.pos.append((begin + end) / 2)
            outBranchData.aimDirs.append(end - begin)
            outBranchData.scales.append(OpenMaya.MVector(1,1,1))

        for j, flower in enumerate(flowers):
            outFlowerData.ids.append(j)
            outFlowerData.pos.append(OpenMaya.MVector(flower[0], flower[2], flower[1]))
            outFlowerData.scales.append(OpenMaya.MVector(1,1,1))

        data.outputValue(LSystemInstanceNode.outBranches).setMObject(outBranchData.obj)
        data.outputValue(LSystemInstanceNode.outFlowers).setMObject(outFlowerData.obj)
        
        data.setClean(plug)
    

kDefaultStringAttrValue = "plants/simple1.txt"

# initializer
def LSystemInstanceNodeInitializer():
    tAttr = OpenMaya.MFnTypedAttribute()
    nAttr = OpenMaya.MFnNumericAttribute()

    #input
    LSystemInstanceNode.angle = nAttr.create("angle", "a", OpenMaya.MFnNumericData.kFloat, 30.0)
    MAKE_INPUT(nAttr)

    LSystemInstanceNode.step = nAttr.create("step", "s", OpenMaya.MFnNumericData.kFloat, 1.0)
    MAKE_INPUT(nAttr)

    stringData = OpenMaya.MFnStringData().create( kDefaultStringAttrValue)
    LSystemInstanceNode.grammarFile = tAttr.create("grammarFile", "g", OpenMaya.MFnData.kString, stringData)
    MAKE_INPUT(tAttr)

    LSystemInstanceNode.iterations = nAttr.create("iterations", "i", OpenMaya.MFnNumericData.kInt, 2)
    MAKE_INPUT(nAttr)

    LSystemInstanceNode.outBranches = tAttr.create("outBranches", "ob", OpenMaya.MFnArrayAttrsData.kDynArrayAttrs)
    MAKE_OUTPUT(tAttr)
    LSystemInstanceNode.outFlowers = tAttr.create("outFlowers", "of", OpenMaya.MFnArrayAttrsData.kDynArrayAttrs)
    MAKE_OUTPUT(tAttr)

    try:
        LSystemInstanceNode.addAttribute(LSystemInstanceNode.angle)
        LSystemInstanceNode.addAttribute(LSystemInstanceNode.step)
        LSystemInstanceNode.addAttribute(LSystemInstanceNode.grammarFile)
        LSystemInstanceNode.addAttribute(LSystemInstanceNode.iterations)
        LSystemInstanceNode.addAttribute(LSystemInstanceNode.outBranches)
        LSystemInstanceNode.addAttribute(LSystemInstanceNode.outFlowers)
        
        LSystemInstanceNode.attributeAffects(LSystemInstanceNode.angle, LSystemInstanceNode.outBranches)
        LSystemInstanceNode.attributeAffects(LSystemInstanceNode.step, LSystemInstanceNode.outBranches)
        LSystemInstanceNode.attributeAffects(LSystemInstanceNode.grammarFile, LSystemInstanceNode.outBranches)
        LSystemInstanceNode.attributeAffects(LSystemInstanceNode.iterations, LSystemInstanceNode.outBranches)

        LSystemInstanceNode.attributeAffects(LSystemInstanceNode.angle, LSystemInstanceNode.outFlowers)
        LSystemInstanceNode.attributeAffects(LSystemInstanceNode.step, LSystemInstanceNode.outFlowers)
        LSystemInstanceNode.attributeAffects(LSystemInstanceNode.grammarFile, LSystemInstanceNode.outFlowers)
        LSystemInstanceNode.attributeAffects(LSystemInstanceNode.iterations, LSystemInstanceNode.outFlowers)

        print("LSystemInstanceNode initialized!\n")

    except:
        sys.stderr.write( ("Failed to create attributes of LSystemInstanceNode\n") )

# creator
def LSystemInstanceNodeCreator():
    return OpenMayaMPx.asMPxPtr( LSystemInstanceNode() )
