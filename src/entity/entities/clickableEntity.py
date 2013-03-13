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
from java.awt.event import InputEvent
from region.exception import FindExhaustedException
from entity.exception import StateFailedException
from sikuli.Sikuli import sleep

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


    def drag(self, destination):
        
        # Ensure valid
        self.validate()
                
        # Move the mouse to this entity
        self.config.screen.mouseMove(self.region)        
        sleep(0.1) 
        self.config.screen.mouseDown(InputEvent.BUTTON1_MASK)
        sleep(0.4) 
        self.config.screen.mouseMove(destination)
        sleep(0.3)
        self.config.screen.mouseUp(InputEvent.BUTTON1_MASK)
        
        # This entity is no longer valid since it's been dragged
        self.invalidate()
        
  
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