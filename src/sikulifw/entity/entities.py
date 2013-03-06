"""
Copyright (c) 2013, SMART Technologies ULC 
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:
á Redistributions of source code must retain the above copyright notice,
this list of conditions and the following disclaimer.
á Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.
á Neither the name of the Copyright holder (SMART Technologies ULC) nor
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

from . import Entity
from org.sikuli.script import OS, KeyModifier, Key, Location
import re
from java.awt.event import InputEvent
from sikulifw.region.exception import FindExhaustedException
from sikulifw.entity.exception import StateFailedException
from sikuli.Sikuli import sleep
from sikulifw.wrapper import Env
from sikuli.Region import Region
import time
import math
import string



class Application(Entity):
    """ Application Entitiy """
    
    # For borg/singleton pattern
    shared_state = None

    family = True
    pid = None
    applicationProcess = None
    processMonitor = None

    binary = {
              OS.WINDOWS : None, #'SMART Technologies/Education Software/Notebook.exe'
              OS.MAC : None, #'SMART Technologies/Notebook.app'
              OS.LINUX : None #'/opt/SMART Technologies/SMART Notebook/bin/notebook'
            }
    
    workingDir = {
                  OS.WINDOWS : None,
                  OS.MAC : None,
                  OS.LINUX: None,
                }
        
    def __init__(self, *args, **kargs):
        self.__dict__ = self.shared_state # borg pattern, singleton   
        if self.region: return # singleton hackin
                            
        super(Application, self).__init__(None, *args, **kargs)        
    
    def setApplicationProcess(self, process, monitor=True):
        self.applicationProcess = process
        
        match = re.search(r"\(([0-9]*)\)", str(process))
        if match and match.group(1):
            self.pid = int(match.group(1))
        else:
            raise Exception("Unable to match process id")
        
        # Add to performance monitor
        if monitor:            
            self.processMonitor.add(self.pid)
        
        
    def getApplicationProcess(self):
        return self.applicationProcess
    
    def getPid(self):
        return self.pid

    def getBinary(self, os, osVersion, arch):
        return self.parsePath(os, osVersion, arch, self.binary[os])
        
    def getWorkingDir(self, os, osVersion, arch):
        if self.workingDir[os]:
            return self.parsePath(os, osVersion, arch, self.workingDir[os])
        else:
            return None

    def parsePath(self, os, osVersion, arch, path):        
        if path[:1] == '/' or path[:3].lower() == 'c:\\':
            pass # absolute path        
        elif os == OS.WINDOWS and (arch == 'x64' or osVersion == "XP"):
            path = path.replace('<%Program Files%>', 'c:/Program Files')    
        elif os == OS.WINDOWS and arch == 'x86':
            path = path.replace('<%Program Files%>', 'c:/Program Files (x86)')
        elif os == OS.MAC:
            path = path.replace('<%Program Files%>', '/Applications')
        
        return path
       
    

class Window(Entity):
    """ Window Entitiy """
        
    def __init__(self, *args, **kargs):        
        super(Window, self).__init__(*args, **kargs)
        #self.validate()  # Delay until sub-entity is called            

            
        


"""        try:
            while True:
                self.__updateRegion()
        except UpdateFailure, e:
            self.logger.info(" vanished", entity=self)
            return self"""


class Label(Entity):
    
    statusCascade = True
    filter = None
    
    def addFilter(self, filter):
        self.filter = filter
    
    def getText(self):
        
        self.validate()
        
        text = self.region.text()
        self.logger.trace("text=%s" % text)
                                                        
        return text
    
    def getValue(self):                    
        
        value = self.getText()
        
        if self.filter:
            value = self.filter(value).getValue()
        
        self.logger.trace("postFilter=%s" % value)
        
        return value
                

class ClickableEntity(Entity):
    
    postState = None
    statusCascade = True
    
    clickStrategy = None #StandardClick() - Use dep injection now
    #clickStrategy = ClickAfterVisualChange()
    
    # Image State
    STATE_NONE = ""    
    STATE_DISABLED = "disabled"
    STATE_DISABLED_SELECTED = "disabled-selected"
    STATE_SELECTED = "selected"
    STATE_UNSELECTED = "unselected"
    
    LEFT_MOUSE = InputEvent.BUTTON1_MASK
    RIGHT_MOUSE = InputEvent.BUTTON3_MASK
    
    @classmethod
    def setDefaultClickStrategy(cls, clickStrategy):
        cls.clickStrategy = clickStrategy
    
    def __init__(self, parent, invalidate=False, clickStrategy=None, *args, **kargs):        
        super(ClickableEntity, self).__init__(parent, *args, **kargs)
        
        self.clickInvalidate = invalidate
        
        if clickStrategy:
            self.clickStrategy = clickStrategy            


    def mouseMove(self,  resultArgs=None, resultParent=None):
        
        # Ensure valid
        self.validate()
        
        # Move the mouse to this entity
        self.config.screen.mouseMove(self.region)
        
        # Use result args are supplied use them, else use the ones supplied when the object was created
        resultArgs = resultArgs if resultArgs else self.resultArgs
        
        return self.getResult(resultParent=resultParent, **resultArgs)
  
    def click(self, callback=None, callbackContext=None, resultArgs=None, postState=None, verifyClick=True, resultParent=None, button=LEFT_MOUSE, **kargs):
        """ Select a element (eg. Button) """
         
        # Ensure valid
        self.validate()
        
        # Uses composition so that click behavior can be changed on a per-entity basis
        self.clickStrategy.click(self)
        self.logger.info("clicked")
                
        # Assert the state of the button after clicking it
        self.assertState(postState)
        
        # invalidate 
        if self.clickInvalidate:
            self.invalidate(self)
        
        # override callback with callback from this function
        callback = callback if callback else self.callback        
        callbackContext = callbackContext if callbackContext else self.callbackContext
        
        # perform callback
        if callback and callbackContext:
            callback(callbackContext)
        elif callback:
            callback(self)
        
        # Update context with update pairs --- What for?! What does this do?
        if callbackContext and self.updatePairs:    
            for pair in self.updatePairs:
                callbackContext.__dict__[pair[0]] = pair[1]
        
        # Use result args are supplied use them, else use the ones supplied when the object was created
        resultArgs = resultArgs if resultArgs else self.resultArgs
        
        return self.getResult(resultParent=resultParent, **resultArgs)     
       

    def assertState(self, state=None):

        # Ensure valid
        self.validate()

        # if not specified in method, default to constructor value
        if not state and self.postState:
            state = self.postState
            
        # Check if there is a post state of clicking this button
        if state:
            self.logger.trace("trying to verify state=%s" % state)
            
            # try and click the button     
            # TODO: (tt::) next line is broken because regionFinder is probably not a static function, can't call it like this       
            ir = Entity.regionFinder(self, region=self.region, state=state) # image region of the button                
            try:
                region = ir.find()                
                
            except FindExhaustedException, e:
                raise StateFailedException("incorrect state [%s]" % state)        
        
            self.logger.info('verified state state=%s %%s' % state, self.logger.getFormatter()(ir).showBaselines())
            #self.logger.info('verified state state=%s %%s %%s' % state, Formatter("Match").addImages(region, "actual"), Tag(ir.getImageNames(state=state),"baseline"))
            #self.logger.info('verified state [["' + state + '"](' + self.logger.region(region=region) + ':actual,' + ','.join(self.logger.image(ir.getImageNames(state=state), tag="baseline")) + ')]')
        
        return self.parent
    
    def setClickStrategy(self, clickStrategy):
        self.clickStrategy = clickStrategy       




class Radio(ClickableEntity):
    """ Radio Entity """

    def __init__(self, parent, *args, **kargs):
        super(Radio, self).__init__(parent, *args, **kargs) 

class CheckBox(ClickableEntity):
    """ CheckBox Entity """
    
    def __init__(self, parent, *args, **kargs):
        super(CheckBox, self).__init__(parent, *args, **kargs)    

class Button(ClickableEntity):
    """ Button Entity """
    
    def __init__(self, parent, *args, **kargs):
        super(Button, self).__init__(parent, *args, **kargs)
           
class TextBox(Entity):
    """ Textbox Entity """
    
    statusCascade = True
    
    def __init__(self, parent, *args, **kargs):
        super(TextBox, self).__init__(parent, *args, **kargs)

    def type(self, text, callback=None, context=None, verify=True, **kargs):
        """ Select a element (eg. Button) """
         
        # Ensure valid
        self.validate()

        # Sometimes click isn't registered, implement our own version of click
        self.config.screen.mouseMove(self.region.getClickLocation())
        sleep(0.5)
        self.config.screen.mouseDown(InputEvent.BUTTON1_MASK)
        sleep(0.8)
        self.config.screen.mouseUp(InputEvent.BUTTON1_MASK)
        sleep(0.5)
        keyMod = KeyModifier.CTRL
        import os
        if os._name == 'posix':
            keyMod = KeyModifier.CMD
        self.config.screen.type(None, "a", keyMod)
        sleep(0.5)
        self.config.screen.type(Key.BACKSPACE)
        sleep(0.5)
     
        """
        Note: Config.screen.type() or paste() behaves differently in Windows and Mac regarding clipboard
        
        In Mac: 
        Through testing, found that Config.screen.type(text), then copy the text somehow does not store the text in the clipboard.
        if we want to retrieve the text properly in Mac from clipboard later, then we have to use "Config.screen.paste(text).
        
        However, if we use paste() here, then Mac response "prompt adding title page" does not recognize that text has been pasted in the edit
        box and the "Add" button will not enabled. (In Mac, you need to actually type something in that edit box for the "Add" button 
        to be enabled. A bug is raised.
        
        In Windows:
        Both Config.screen.type()/Config.screen.paste() and copy the text STORE the text in the clipboard properly. And Response "prompt adding
        title page" recognize the pasted text in the edit box and the "Add" button is enabled properly
        """
        self.config.screen.paste(text) 
        sleep(1.0)
     
        if verify:
            self.config.screen.type(None, "a", keyMod)
            sleep(1.0)
            self.config.screen.type(None, "c", keyMod)
            sleep(1.0)
            actual = Env.getClipboard()
            actual = string.replace(actual,'\r','') # Sometimes copy stuff from Teacher Tools had extra line returns, and new line characters
            actual = string.replace(actual,'\n','')
            self.logger.info('\nactual= %s, text = %s' % (actual, text))
            assert actual == text

        
        self.logger.info('typed ["%s"], on %%s' % (text), self.logger.getFormatter()(self.parent))
        
                
        return self.parent


class DropDown(ClickableEntity):
    """ DropDown Entity """    
    
    def __init__(self, parent, *args, **kargs):
        super(DropDown, self).__init__(parent, *args, **kargs)
     
class ProgressBar(Entity):
    """ Button Entity """
    
    lastChange = None
    
    def __init__(self, parent, *args, **kargs):
        super(ProgressBar, self).__init__(parent, *args, **kargs)
        
    def waitUntilComplete(self, timeout=60, resultArgs={}):
        
        self.validate()
        
        # Convert Match to Region -> workaround: https://bugs.launchpad.net/sikuli/+bug/905435
        r = Region(self.region)
        r.onChange(self.__changed)
        r.observe(FOREVER, background=True) # start observing progress bar
        
        startTime = time.time()
        self.lastChange = time.time()
        # loop while things are still changing        
        while (time.time()-self.lastChange) < timeout:
            sleep(1)
            
        r.stopObserver() # stop observing progress bar
        self.logger.trace("stopped changing after %ds" % (time.time()-startTime))
            
        # try and click the button            
        state = "complete"
        ir = self.regionFinder(self, region=self.region, state=state) # image region of the button                
        try:
            region = ir.find()                                    
        except FindExhaustedException, e:
            raise StateFailedException("incorrect state [%s]" % state)
        else:
            self.logger.info("completed successfully!")
                               
        return self.getResult(**resultArgs)
    
    def __changed(self, event):
        
        # Progress bar has changed        
        self.lastChange = time.time()
        

## Todo: Better solution?
def invalidateDragBar(context):
    context[context.DRAG_BAR].invalidate()


class ScrollBar(Entity):
        
    
    family = True
    UP = ['up', lambda parent, **kargs: Button(parent, context=parent, callback=invalidateDragBar, **kargs)]
    DOWN = ['down', lambda parent, **kargs: Button(parent, context=parent, callback=invalidateDragBar, **kargs)]
    
    DRAG_BAR = ['dragBar', lambda parent, **kargs: Window(parent, **kargs)]
    
    
    def gotoTop(self):        
        self[self.DRAG_BAR].move(self[self.UP].getRegion())
        return self
        
    def gotoBottom(self):
        self[self.DRAG_BAR].move(self[self.DOWN].getRegion())
        return self
        
        
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
    

