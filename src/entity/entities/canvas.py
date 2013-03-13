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


from entity import Entity
from org.sikuli.script import OS, KeyModifier, Key, Location
import re
from java.awt.event import InputEvent
from region.exception import FindExhaustedException
from entity.exception import StateFailedException
from sikuli.Sikuli import sleep
from wrapper import Env
from sikuli.Region import Region
import time
import math
import string
import os
from entity.entities import ScrollBar, Button

class Canvas(Entity):
    
    statusCascade = True
    offsetY = None
    virtualCanvasSize = None
    drawingStrategy = None
    
    HORIZONTAL_SCROLLBAR = [ScrollBar, lambda parent, statusCascade=True, **kargs: ScrollBar(parent,  parentRegion=parent.parent.region, **kargs)]    
    EXTEND_PAGE = ['extendPage', lambda parent, **kargs: Button(parent, invalidate=True, statusCascade=False, **kargs)]
    
    @classmethod
    def setDefaultDrawingStrategy(cls, drawingStrategy):
        cls.drawingStrategy = drawingStrategy
            
    def __init__(self, parent, *args, **kargs):
        super(Canvas, self).__init__(parent, *args, **kargs)
        
        # Need to get region for setting virtual canvas size
        self.validate()
                    
        self.offsetY = 0
        self.virtualCanvasSize = self.region.getH()
        self.drawingStrategy = self.drawingStrategy(self) # Initialize the drawing strategy
        #self[self.HORIZONTAL_SCROLLBAR].gotoTop() Causing validation problems, move elsewhere?
    
    def goto(self, x, y):
        
        self.drawingStrategy.goto(x,y)
        
    def line(self, x1, y1, x2, y2):
                        
        assert x1 >= 0
        assert x2 >= 0
        assert x1 <= self.getW()
        assert x2 <= self.getW()
        
        # make sure we can actually draw this (less than height of canvas)
        assert math.fabs(y1 - y2) <= self.getH()
        
        # Make sure we have the canvas centered in the right place
        self.center(Location(x1,y1))
        self.center(Location(x2,y2))
         
        # Draw stuff
        self.goto(x1,y1)
        self.goto(x2,y2)
        
    def mouseMove(self, x, y):

        # We should never be trying to draw outside the canvas area
        assert x >= 0
        assert y - self.offsetY >= 0
        assert x <= self.getW()
        assert y - self.offsetY <= self.region.getH()       
        
        self.region.mouseMove(Location(self.region.getX() + x, self.region.getY() + y - self.offsetY))
    
    def startDrawing(self):
        #self.logger.trace("Starting to draw..")
        self.region.mouseDown(InputEvent.BUTTON1_MASK)
        
    def stopDrawing(self):
        #self.logger.trace("Stop drawing..")
        self.region.mouseUp(InputEvent.BUTTON1_MASK)
        

    
    def center(self, location):
        
        if isinstance(location, Region):
            self.center(Location(location.getX(), location.getY()))
            self.center(Location(location.getX() + location.getW(), location.getY() + location.getH()))
            return
        else:
            assert isinstance(location, Location)
            
        
        # If offset is too high 
        if location.getY() < self.offsetY:
            steps = math.ceil((self.offsetY - location.getY()) / 10)
            
            for i in range(0, steps):
                self.offsetY -= 10;
                self[Canvas.HORIZONTAL_SCROLLBAR][ScrollBar.UP].click()
         
        # If offset is too low
        if location.getY() > (self.offsetY + self.region.getH()):
            
            # Extend the page if it needs to be
            if location.getY() > self.virtualCanvasSize:
                
                # Get to the bottom of the page
                self[Canvas.HORIZONTAL_SCROLLBAR].gotoBottom()
                
                # Get number of times the page needs to be expanded
                steps = math.ceil((location.getY() - self.virtualCanvasSize) / 200)                
                for j in range(0, steps):
                    self[Canvas.EXTEND_PAGE].click()
                    self.virtualCanvasSize += 200  # Think this is right?
            
                # Start back at the top
                self[Canvas.HORIZONTAL_SCROLLBAR].gotoTop()
                self.offsetY = 0                      
            
            # Move the page down based on the number of 10 pixels increments to the new Y offset
            steps = math.ceil((location.getY() - (self.offsetY + self.region.getH())) / 10)
            for i in range(0, steps):
                self.offsetY += 10;
                self[Canvas.HORIZONTAL_SCROLLBAR][ScrollBar.DOWN].click()
                                
    def on(self):        
        self.drawingStrategy.on()
        
    def off(self):        
        self.drawingStrategy.off()
    
    def setDrawingStrategy(self, drawingStrategy):
        self.drawingStrategy = drawingStrategy(self)
    