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

from config import Config
from log import Logger, DEBUG, INFO, TRACE
from sikuli.Sikuli import sleep
from entity import Entity
from entity.entities import ClickableEntity
from log import EntityLoggerProxy


class KeyNotInArgStorageException(Exception):
    pass

class SikuliFwRfAbstractLib(object):
    """
    Base class for SikuliFramework Application entities, helps bridge SikuliFW with RobotFramework. 
    """
    
    logger = None
    argStore = None
    entity = None
    
    def __init__(self):
        self.argStore = {}
        self.logger = EntityLoggerProxy(self)
    
    def displayConfig(self):
        self.logger.info("%s" % Config.toString())
        
    def validate(self, *args):
        """
        Validates an entity, finding it on the screen
        """        
        
        # Set the context, take it if it's the first in the list        
        try:
            context = self.retrieve(args[0])
            args = args[1:] # Remove the first, ie. pop            
            context.validate() # Validate this first
            
        except KeyNotInArgStorageException:
            context = self.entity        
            
        # Perform lots of clicks and stuff
        for target in args:    
            self.logger.info("[%s] selecting [%s]" % (context, target))
            context = context[target]
            context.validate() # Ensure each is validated
                    
        # Let the entity do the selectin
        return self.store(context)
        

    def select(self, *args):
        
        # Set the context, take it if it's the first in the list        
        try:
            context = self.retrieve(args[0])
            args = args[1:] # Remove the first, ie. pop
        except KeyNotInArgStorageException:
            context = self.entity        
            
        # Perform lots of clicks and stuff
        for target in args:    
            self.logger.info("[%s] selecting [%s]" % (context, target))
            context = context[target]
                    
        # Let the entity do the selectin
        return self.store(context)
    
    def click(self, *args):
        
        # Set the context, take it if it's the first in the list        
        try:
            context = self.retrieve(args[0])
            args = args[1:] # Remove the first, ie. pop
        except KeyNotInArgStorageException:
            context = self.entity
        
        # Perform lots of clicks and stuff
        for target in args:            

            target = str(target)
            
            self.logger.info("[%s] executing [%s]" % (context, target))
            context = context[target]

            # Perform the click 
            if isinstance(context, ClickableEntity):
                context = context.click() 
 
        return self.store(context)
    
    
    def type(self, *args):

        try:
            # try format (context, target, text)
            context = self.retrieve(args[0])
            targetArgs = [args[1],]
            text = args[2]
        except KeyNotInArgStorageException:
                    
            # Except Try format (value, targetArg0..N)
            try:
                context = self.retrieve(args[1])
                targetArgs = args[2:]
            except KeyNotInArgStorageException:
                context = self.entity
                targetArgs = args[1:]
            
            text = args[0]    
            
            
        # Try and find target
        for target in targetArgs:            
            context = context[target]            
                    
        return self.store(context.type(text))

    def waitUntilVanish(self, target=None, timeout=None):
        
        if target:
            # Set the context, take it if it's the first in the list        
            try:
                context = self.retrieve(target)
            except KeyNotInArgStorageException:
                context = self.entity[target]
        elif self.entity:
            context = self.entity
        else:
            raise Exception("Unable to determine context")     
        
        kargs = {}
        
        # Add a timeout if it's specified
        if timeout:
            kargs['timeout'] = timeout
        
        return self.store(context.waitUntilVanish(**kargs))
    
    def waitUntilAppears(self, target=None, timeout=None):
        
        if target:
            # Set the context, take it if it's the first in the list        
            try:
                context = self.retrieve(target)
            except KeyNotInArgStorageException:
                context = self.entity[target]
        elif self.entity:
            context = self.entity
        else:
            raise Exception("Unable to determine context")     
        
        kargs = {}
        
        # Add a timeout if it's specified
        if timeout:
            kargs['timeout'] = timeout
        
        return self.store(context.waitUntilAppears(**kargs))
            
    def showConfig(self):        
        self.logger.info(Config.toString())
    
    def setLogLevel(self, level):
        """ Change the level of detail that is logged """
        
        level = str(level)
        
        if str.lower(level) == 'info':
            Logger.setLevel(INFO)
        elif str.lower(level) == 'debug':
            Logger.setLevel(DEBUG)
        elif str.lower(level) == 'trace':
            Logger.setLevel(TRACE)
        else:
            raise Exception("Logging level [%s] is not supported" % level)

    def setScreenshotLogLevel(self, level):
        """ Change the level of detail that is logged """
        
        level = str(level)
        
        if str.lower(level) == 'INFO':
            Config.setScreenshotLoggingLevel(INFO)
        elif str.lower(level) == 'debug':
            Config.setScreenshotLoggingLevel(DEBUG)
        elif str.lower(level) == 'trace':
            Config.setScreenshotLoggingLevel(TRACE)
        else:
            raise Exception("Screenshot logging level [%s] is not supported" % level)
            
            
    def retrieve(self, key):
        """ Retrieve an argument from storage using a key """
        
        # assert the key is a string
        assert isinstance(key, str) or isinstance(key, unicode)
        
        try:
            self.logger.info("Resolved Entity=%%s", self.logger.getFormatter()(self.argStore[key]))
            return self.argStore[key]
        except KeyError:
            
            # We cannot find the key in storage
            raise KeyNotInArgStorageException()
    
    def store(self, var):
        """ Store an argument and return the key """
        
        # The key becomes the type of variable
        key = str(type(var))
        
        self.argStore[key] = var
        return key
    
    def sleep(self, duration):
        """
        Pauses the script for N seconds
        """
                
        sleep(int(duration))
    
    def captureScreen(self):
        self.logger.info("Screen=%%s", self.logger.getFormatter()(Config.screen))
        
    def assertBaseline(self, *args):
        
        # Set the context, take it if it's the first in the list        
        try:
            context = self.retrieve(args[0])
            args = args[1:] # Remove the first, ie. pop
        except KeyNotInArgStorageException:
            context = self.entity            
            
        context.assertBaseline(args[0])

    def assertEquals(self, *args):
        
        # Set the context, take it if it's the first in the list        
        try:
            context = self.retrieve(args[0])
            args = args[1:] # Remove the first, ie. pop
        except KeyNotInArgStorageException:
            context = self.entity            
            
        context.assertEquals(args[0])
            
    
    def convertUnicodeToAscii(self, *args):
        
        fixedArgs = []
        
        for arg in args:
            arg = str(arg) if isinstance(arg, unicode) else arg
            fixedArgs.append(arg)
        
        return fixedArgs
            
        

if __name__ == "__main__":
    
    sikulifwLib = RfSikuliFwLib()

