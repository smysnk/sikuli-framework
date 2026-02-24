"""
Copyright (c) 2013, SMART Technologies ULC 
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:
* Redistributions of source code must retain the above copyright notice,
this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.
* Neither the name of the Copyright holder (SMART Technologies ULC) nor
the names of its contributors (Joshua Henn) may be used to endorse or
promote products derived from this software without specific prior
written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER (SMART Technologies
ULC) "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import pickle
import re
import os
from compat import execfile_compat, text_type
from config import BACKEND_SIKULIGO, Config
import time

if Config.backend == BACKEND_SIKULIGO:
    from adapters.sikuligo_backend import Location, Pattern, Region, Screen

    class InputEvent(object):
        BUTTON1_MASK = "left"

    def sleep(seconds):
        time.sleep(seconds)
else:
    from org.sikuli.script import Location, Pattern
    from sikuli import Screen, Region
    from java.awt.event import InputEvent
    from sikuli.Sikuli import sleep

class Transform(object):
    """ 
    Allows for transforms to be stored in PNG files.  Transforms are used to control how the PNG 
    is matched and how the pre-match and post-match regions are treated. 
    
    """
        
    logger = None
    
    transforms = None
    regionsMatched = None
    entity = None
    context = None
    
    # CONTEXT TYPES
    CONTEXT_PREVIOUS = "PREVIOUS"    
    CONTEXT_NEXT = "NEXT"
    CONTEXT_CURRENT = "CURRENT"    
    CONTEXT_FINAL = "FINAL"
    CONTEXT_MATCH = "MATCH"
    CONTEXT_ENTITY = "ENTITY"
    
    
    @classmethod
    def setLogger(cls, logger):
        cls.logger = logger
        
    def __init__(self, source, entity=None, regionsMatched=None, context=None, *args, **kargs):
        """ Returns a pattern and attributes given a filename """        
        super(Transform, self).__init__(*args, **kargs)

        transforms = None
        self.regionsMatched = regionsMatched
        self.entity = entity if entity else self
        self.context = context
        self.logger = self.__class__.logger(self)
        
        defaultTransforms = { \
                        Transform.CONTEXT_PREVIOUS: [ RegionNearby(10) ], \
                        Transform.CONTEXT_CURRENT: [], \
                        Transform.CONTEXT_NEXT: [], \
                        Transform.CONTEXT_FINAL: [], \
                        Transform.CONTEXT_MATCH: [], \
                        Transform.CONTEXT_ENTITY: []
                    }     
        

        # If we have a string, a path is supplied to png
        if isinstance(source, text_type):
            
            transforms = defaultTransforms
            
            # Try and get extra attributes
            try:            
                tempDict = {}
                execfile_compat(source[:-3] + "py", tempDict)
                transforms = tempDict['transforms']                
                assert isinstance(transforms, dict)
                
            except TypeError: # If doesn't contain a tEXt section
                pass   
            except AssertionError:
                pass # assertion raised- invalid format?                
                self.logger.warn("Expecting dictionary got [%s] instead, possibly corrupted PNG attributes section in file [%s], using defaults" % (type(transforms), source))
            except IOError:
                pass # File doesn't exist
                                        
        # Otherwise a dictionary should be supplied
        elif isinstance(source, dict):
            transforms = source
        
        if (not isinstance(transforms, dict)):
            self.logger.warn("Unknown PNG transforms format, using defaults")
            transforms = defaultTransforms            
                
        self.transforms = transforms        
            
    def apply(self, operand, context, override=None, *args, **kargs):
        
        # If the context is not valid just return the operand
        if not self.transforms.get(context):
            return operand
        
        # Allow for override on the operand
        if len(self.transforms[context]) and override:
            operand = override
                
        # Apply the transforms
        for transform in self.transforms[context]:            
            result = transform.apply(operand, previousMatches=self.regionsMatched, entity=self.entity, context=self, *args, **kargs)
            
            self.logger.debug("%s Applied %s transform, %%s -> %%s " % (context, transform), self.logger.getFormatter()(operand), self.logger.getFormatter()(result))            
            
            operand = result
            
        return operand

    def formatPrefix(self, *args, **kargs):
        
        return "[PNGTransforms] "
    
    def __str__(self):
        
        if self.context:
            return str(self.context) + "->%s" % (self.__class__.__name__)
        else:
            return self.__class__.__name__

class EntityTransform(object):
    
    config = None
    clickStrategy = None    
    context = None
    
    @classmethod
    def setConfig(cls, config):
        cls.config = config
    
    def apply(self, *args, **kargs):
        raise Exception("must be subclassed")
    
    def __str__(self):
        
        if self.context:
            return str(self.context) + "->%s" % (self.__class__.__name__)
        else:
            return self.__class__.__name__    

class ClickableEntityClickStrategy(EntityTransform):
        
    def __init__(self, clickStrategy):        
        self.clickStrategy = clickStrategy
        
    def apply(self, operand, context=None, *args, **kargs):
        
        self.context = context
        self.logger = self.config.getLogger()(self)
        
        # Wire up click strategy
        self.clickStrategy.setScreen(self.config.getScreen())
        self.clickStrategy.setLogger(self.config.getLogger()(self))
        
        self.logger.trace("setting click strategy to %s" % self.clickStrategy)         
        operand.setClickStrategy(self.clickStrategy) 
        

class PatternSimilarity(object):
    
    similarity = None
    
    def __init__(self, similarity):        
        self.similarity = similarity
    
    def apply(self, operand, *args, **kargs):        
        return operand.similar(self.similarity)
        
    def __str__(self, *args, **kwargs):
        return "%s similarity=%d" % (self.__class__.__name__, self.similarity)        
        
class PatternTargetOffset(object):
    """ Depreciated by RegionClick offset """
    dx = 0
    dy = 0
    
    def __init__(self, dx, dy):        
        self.dx = dx
        self.dy = dy
    
    def apply(self, operand):
        return operand.targetOffset(self.dx, self.dy)

    def __str__(self, *args, **kwargs):
        return "%s dx=%s dy=%s" % (self.__class__.__name__, self.dx, self.dy)

class ActionClick(object):
    
    x = 0
    y = 0
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def apply(self, operand, *args, **kargs):
        #print operand.getX() + self.x, operand.getY() + self.y
        #operand.click(operand.getX() + self.x, operand.getY() + self.y)
        #operand.click(500,500)
        operand.mouseMove(Location(operand.getX() + self.x, operand.getY() + self.y))
        operand.mouseDown(InputEvent.BUTTON1_MASK)
        sleep(0.5)
        operand.mouseUp(InputEvent.BUTTON1_MASK)
        
        return operand
    
    def __str__(self, *args, **kargs):
        return "%s x=%s y=%s" % (self.__class__.__name__, self.x, self.y)

class RegionClickOffset(object):
    
    dx = None
    dy = None

    def __init__(self, dx, dy):
        self.dx = dx
        self.dy = dy
        
    def apply(self, operand, *args, **kargs):
        
        operand.setClickOffset(Location(self.dx, self.dy))

        return operand
    
class RegionMorph(object):
    
    dx1 = None
    dy1 = None
    dx2 = None
    dy2 = None

    def __init__(self, dx1, dy1, dx2, dy2):
        self.dx1 = dx1
        self.dy1 = dy1
        self.dx2 = dx2
        self.dy2 = dy2
        
    def apply(self, operand, *args, **kargs):
        
        x1 = operand.getX() + self.dx1
        y1 = operand.getY() + self.dy1
        x2 = operand.getX() + operand.getW() + self.dx2
        y2 = operand.getY() + operand.getH() + self.dy2
                
        operand = Region(x1, y1, x2-x1, y2-y1) #morph

        return operand

    def __str__(self, *args, **kwargs):
        return "%s dx1=%d dy1=%d dx2=%d dy2=%d" % (self.__class__.__name__, self.dx1, self.dy1, self.dx2, self.dy2)        
        
class RegionScreen(object):
    
    config = None
    
    @classmethod
    def setConfig(cls, config):
        cls.config = config
    
    def apply(self, operand, *args, **kargs):
        
        return self.config.getScreen()   
    
    
class RegionPreviouslyMatched(object):
    """ Will get the area of previous matches, including the entities parent region """
    
    parent = None
    
    def __init__(self, parent=False):
        self.parent = parent        
            
    def apply(self, operand, previousMatches=None, entity=None, *args, **kargs):
                    
        # Include context's parent in previous matched
        if self.parent and entity.parent:
            parentRegion = [entity.parent.region]
        else:
            parentRegion = []
            
        if len(previousMatches + parentRegion) == 0:
            raise Exception("Cannot find any previous regions")
        
        return Region(previousMatches + parentRegion + [operand])
    
class RegionalTransform(object):    

    value = None
    
    def __init__(self, value=None):
        self.value = value
    
    def apply(self, operand, previousMatches=None, context=None, *args, **kargs):
               
        # Don't transform if we're working with screen
        if isinstance(operand, Screen):
            return operand
        else:
            return self.algorithm(operand, previousMatches=previousMatches, *args, **kargs)
    
    def __str__(self, *args, **kwargs):
        return "%s value=%s" % (self.__class__.__name__, self.value)
           
class RegionMaxMinMatched(RegionalTransform):    
    """ Depreciated """
            
    def algorithm(self, operand, previousMatches=None, *args, **kargs):
                
        return Region(previousMatches)
    
class RegionAbove(RegionalTransform):
            
    def algorithm(self, operand, *args, **kargs):
        
        if self.value:        
            operand = Region(operand).above(self.value)
        else:
            operand = Region(operand).above()
        
        #operand = Region(operand.getX()-(self.proximity/2), operand.getY(), operand.getW()+self.proximity, operand.getH())                                                    
        return operand

class RegionBelow(RegionalTransform):
        
    def algorithm(self, operand, *args, **kargs):
        
        if self.value:
            operand = Region(operand).below(self.value)
        else:
            operand = Region(operand).below()                                
        
        
        #operand = Region(operand.getX()-(self.proximity/2), operand.getY(), operand.getW()+self.proximity, operand.getH())                                                    
        return operand

class RegionRight(RegionalTransform):
        
    def algorithm(self, operand, *args, **kargs):

        if self.value:
            operand = Region(operand).right(self.value)
        else:
            operand = Region(operand).right()
        
        #operand = Region(operand.getX(), operand.getY()-(self.proximity/2), operand.getW(), operand.getH()+self.proximity)        
        return operand

class RegionLeft(RegionalTransform):


    def algorithm(self, operand, *args, **kargs):
        
        if self.value:
            operand = Region(operand).left(self.value)
        else:
            operand = Region(operand).left()
        
        #operand = Region(operand.getX(), operand.getY()-(self.proximity/2), operand.getW(),operand.getH()+self.proximity)        
        return operand

class RegionNearby(RegionalTransform):

    def algorithm(self, operand, *args, **kargs):
        
        if self.value:
            operand = Region(operand).nearby(self.value)
        else:
            operand = Region(operand).nearby()        
        
        #operand = Region(operand.getX()-(self.proximity/2), operand.getY()-(self.proximity/2), operand.getW()+self.proximity, operand.getH()+self.proximity)
        return operand


class RegionParent(RegionalTransform):
    
    def algorithm(self, operand, entity=None, *args, **kargs):
     
        recurseCount = self.value if self.value else 1
        
        # Go up N parents
        try:
            parentRegion = entity
            for i in range(0, recurseCount):
                parentRegion = parentRegion.parent if parentRegion.parent != None else parentRegion
        finally:    
            pass            
            
        return parentRegion.region    

class RegionLimitByParent(RegionalTransform):
    """ Limit region by it's Nth parent  """
    
    def algorithm(self, operand, entity=None, *args, **kargs):
        
        recurseCount = self.value if self.value else 1
        
        # Go up N parents
        try:
            parentRegion = entity
            for i in range(0, recurseCount):
                parentRegion = parentRegion.parent if parentRegion.parent != None else parentRegion
        finally:
            pass
            
        return operand.limit(parentRegion.region)


        """ if context == Attributes.TYPE_SEARCH_PREV:
                    # Check if we have a nearby attributes
                    nearbyAttrib = False
                    for attrib in self.attribs:            
                        if (attrib[0] == Attributes.TYPE_SEARCH_PREV) and (attrib[1]['value'] == self.SPACIAL_NEARBY):
                            nearbyAttrib = True
                    
                    # If not default to proximity 10
                    if not nearbyAttrib:
                        self.attribs.append([context, {'value':self.SPACIAL_NEARBY, 'proximity':10}])        
        """
        
        """
        for attrib in self.attribs:
            
            # Only appliciable to TYPE_SEARCH context
            if (context == self.CONTEXT_CURRENT) and (attrib[0]:
                assert isinstance(newResult, Pattern)                
                newResult = newResult.similar(attrib[1]['value'])
            
            elif (attrib[0] == context) and not isinstance(newResult, Screen): # don't perform spacial operators on Screen
                               
                proximity = attrib[1].get('proximity', 50) # proximity around region
                limit = attrib[1].get('limit', 9999) # limit around region
                
                if attrib[0]
                elif attrib[1]['value'] == self.SPACIAL_RIGHT:
                    newResult = Region(newResult).right(limit)
                    newResult = Region(newResult.getX(), newResult.getY()-(proximity/2), newResult.getW(),newResult.getH()+proximity)
                elif attrib[1]['value'] == self.SPACIAL_LEFT:
                    newResult = Region(newResult).left(limit)
                    newResult = Region(newResult.getX(), newResult.getY()-(proximity/2), newResult.getW(),newResult.getH()+proximity)
                elif attrib[1]['value'] == self.SPACIAL_NEARBY:
                    newResult = Region(newResult).nearby(limit)
                    newResult = Region(newResult.getX()-(proximity/2), newResult.getY()-(proximity/2), newResult.getW()+proximity,newResult.getH()+proximity)
                else:
                    raise Exception("Unknown spacial search %s" % attrib[1]['value'])
     
        #self.logger.debug("[%s](%s) set similarity to [%1.2f]" % (filename, self.log.image(filename), attrib[1]['value']))
        return newResult

    def formatPrefix(self, *args, **args):
        
        return "[AttributeLoader] "

             
             
           """  
            
