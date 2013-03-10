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

from sikuli.Sikuli import sleep
from org.sikuli.script import Pattern
from java.awt.event import InputEvent

class ClickStrategy(object):
    
    screen = None
    logger = None
        
    @classmethod
    def setScreen(cls, screen):
        cls.screen = screen
        
    @classmethod
    def setLogger(cls, logger):
        cls.logger = logger
    
    def __init__(self):
        pass
    
    def click(self, *args, **args):        
        raise Exception("Must be subclassed")

class StandardClick(ClickStrategy):

    def __init__(self):        
        super(StandardClick, self).__init__()

    
    def click(self, entity, button=InputEvent.BUTTON1_MASK):
        self.screen.mouseMove(entity.getRegion().getClickLocation())
        sleep(0.1) 
        self.screen.mouseDown(button)               
        sleep(1)
        self.screen.mouseUp(button)

class QuickClick(ClickStrategy):
    """
    Mac requires quick click in order to disply the pop up menus
    """

    def __init__(self):        
        super(QuickClick, self).__init__()

    
    def click(self, entity, button=InputEvent.BUTTON1_MASK):
        self.screen.mouseMove(entity.getRegion().getClickLocation())
        sleep(0.1) 
        self.screen.mouseDown(button)               
        self.screen.mouseUp(button)
        

class ClickAfterVisualChange(ClickStrategy):
    
    assertStateChanged = None
    
    def __init__(self, assertStateChanged=False):        
        super(ClickAfterVisualChange, self).__init__()
        
        self.assertStateChanged = assertStateChanged
                    
    def click(self, entity, button=InputEvent.BUTTON1_MASK):

        
        # click
        self.screen.mouseMove(entity.getRegion().getClickLocation())
        sleep(0.5)        
        
        # Get the state of the button before we click
        state = self.screen.capture(entity.getRegion())
        #sleep(0.2)        
        
        self.screen.mouseDown(button)
        sleep(0.5)
        
        # Wait for button to change its appearnce because we're clicking on it
        if entity.getRegion().waitVanish(Pattern(state).similar(1.0), 0.7):                
            sleep(0.2)
        else:
            if self.assertStateChanged:
                raise Exception("State did not change")
            else:
                self.logger.warn("State did not change")
            
        self.screen.mouseUp(button)
        sleep(0.5)

