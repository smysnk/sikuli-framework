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

from entity.entity import Entity
from org.sikuli.script import KeyModifier, Key
import re
from java.awt.event import InputEvent
from sikuli.Sikuli import sleep
from wrapper import Env
from sikuli.Region import Region
import string
from org.sikuli.basics import OS

class TextBox(Entity):
    """ Textbox Entity """
    
    statusCascade = True
    
    def __init__(self, parent, *args, **kargs):
        super(TextBox, self).__init__(parent, *args, **kargs)
        
    def assertEquals(self, expectedText):
        
        # If we're on MAC, use CMD instead of CTRL
        if Env.getOS() == OS.MAC:
            keyMod = KeyModifier.CMD
        else:
            keyMod = KeyModifier.CTRL
        
        # Select 
        self.config.screen.type(None, "a", keyMod)
        sleep(0.5)
        
        self.config.screen.type(None, "c", keyMod)
        sleep(0.5)
        
        clipboardContents = Env.getClipboard()        
        if clipboardContents != expectedText:
            self.logger.error("Clipboard contents [%s] does not match expected value of [%s]" % (clipboardContents, expectedText))
            raise Exception()
        else:
            self.logger.trace("Verified clipboard contents [%s] equals [%s]" % (clipboardContents, expectedText))
    
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
        
        # If we're on OSX, use CMD instead of CTRL
        if Env.getOS() == OS.MAC:
            keyMod = KeyModifier.CMD
        else:
            keyMod = KeyModifier.CTRL        
            
        # Select 
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
            clipboardContents = Env.getClipboard()
            clipboardContents = string.replace(clipboardContents,'\r','')
            clipboardContents = string.replace(clipboardContents,'\n','')
            
            if clipboardContents != text:
                self.logger.error("Clipboard contents [%s] does not match expected value of [%s]" % (clipboardContents, text))
                raise Exception()
            else:
                self.logger.trace("Verified clipboard contents [%s] equals [%s]" % (clipboardContents, text))

        
        self.logger.info('typed ["%s"], on %%s' % (text), self.logger.getFormatter()(self.parent))
        
        return self.parent

