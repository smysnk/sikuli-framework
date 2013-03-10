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

import time
import shutil
import os
from sikuli.Sikuli import getImagePath, capture
import inspect
from org.sikuli.script import ImageLocator, Pattern, FindFailed, Env
from java.io import FileNotFoundException
from md5 import md5
from sikulifw.region.exception import ImageSearchExhausted,\
    FindExhaustedException
from sikulifw.entity.exception import UpdateFailureException,\
    TookTooLongToVanishException, TookTooLongToAppearException
import re
from java.awt.event import InputEvent

class Entity(object):
    """
    Superclass of all SikuliFramework entities.
    When validated each entity has a defined region on the Screen.
    All entities have parents, except for the Application entity (see entities.py).
    To perform most functions on an entity it must be validated first via validate().
    """
    
    STATUS_INVALID = "invalid"
    STATUS_VALID = "valid"
    
    logger = None       # logger instance
    config = None
    
    timeout = 60      # time allowed for this entity to initialize
    baseline = None     # baseline images
    
    subEntity = None   # is sub-entity? eg a button, created by a window would be a sub-entity
    caller = None       # Who was the one who created this entity?
    
    parent = None       # parent of this entity
    resultParent = None # parent of the result of getResult()
    
    region = None       # region of this entity
    parentRegion = None # region to search for this entity in, defaults to parent
    name = None         # name of this entity
    className = None    # class name of this entity
    result = None       # result of this entity    
    instances = None      # instances of sub-entities
    regionFinder = None  #
    
    callback = None
    callbackContext = None
    updatePairs = None
    
    family = False
    
    status = STATUS_INVALID # current status of this entity
    statusCascade = False    # is state cascade to parent? (ie. An entity gets invalidated, does it's parent get affected?)
    
    resultArgs = None
    
    regionFinderStrategy = None
    searcherStrategy = None
    multiResultProxyStrategy = None

    @classmethod
    def setSearcherStrategy(cls, searcherStrategy):
        cls.searcherStrategy = searcherStrategy
    
    @classmethod
    def setRegionFinderStrategy(cls, regionFinderStrategy):
        cls.regionFinderStrategy = regionFinderStrategy

    @classmethod
    def setMultiResultProxyStrategy(cls, multiResultProxyStrategy):
        cls.multiResultProxyStrategy = multiResultProxyStrategy    
    
    @classmethod
    def setLogger(cls, logger):
        cls.logger = logger
        
    @classmethod
    def setConfig(cls, config):
        cls.config = config        
    
    def __init__(self, parent, caller=None, timeout=None, name=None, result=None, statusCascade=None, parentRegion=None, resultArgs=None, callback=None, context=None, updatePairs=None, resultParent=None, *args, **kargs):
        
        super(Entity, self).__init__(*args, **kargs) # Needed for handleable dialogs super
            
        self.instances = {}
                
        if not name: # if name is supplied then this is a sub-entity
            self.subEntity = False
            self.name = self.__class__.__name__
            self.className = self.__class__.__bases__[0].__name__
        else:
            self.subEntity = True
            self.name = name                
            self.className = self.__class__.__name__
                
        self.parent = parent        
        self.logger = self.__class__.logger(self) # initiate logger
        self.logger.trace("created")
        
        # Use class parent region, if not set by constructor
        if parentRegion:
            self.parentRegion = parentRegion
        
        # Configure resulting action
        if result:                  
            if isinstance(result, tuple):
                self.result = result[0]
                self.resultParent = result[1]              
            elif isinstance(result, list):
                self.result = self.multiResultProxyStrategy(self.parent, result, self) # For clickable entities we want the parents, parent
            else:
                self.result = result
        elif not self.result: # not set to anything, set it to parent at least
            self.result = self.parent
        
        # Subclassed might have override
        if statusCascade != None:
            self.statusCascade = statusCascade
            
        if resultParent:
            self.resultParent = resultParent
            
        self.callback = callback
        self.context = context          
        
        if updatePairs:
            self.updatePairs = updatePairs  
        
        # Use result args supplied, if none initialize to blank
        self.resultArgs = resultArgs if resultArgs else {}        
        self.caller = caller
        
        if timeout:
            self.timeout = timeout
            
        self.regionFinder = Entity.regionFinderStrategy(self)
            
            
    def __getitem__(self, key):
        """
        Initialize entity if being accessed for the first time, otherwise existing instance
        """

        KEY_TYPE_NAMED_CLASS = 'namedClass'     # Used for "window" type entities usually 
        KEY_TYPE_GENERIC_CLASS = 'genericCLass' # Used for sub-entities such as buttons, textboxes, etc.

        
        # Support searching
        if isinstance(key, str) or isinstance(key, unicode):                        
            searcher = self.searcherStrategy()
            searcher.add(self)
            searchResult = searcher.search(key)            
            key = searchResult.getEntity() 
              
            # Expecting key = [<keyname>, <class>, <args>]
        if isinstance(key[0], str) or isinstance(key[0], unicode): # If the key name is a string, it is usually a sub-entity
            keyName = key[0]
            keyType = KEY_TYPE_GENERIC_CLASS
            keyClass = key[1] # If the name is specified as a string, it is expected the second item in the array is the class
        else: # Keyname must be a class, this key type is usually a "window" entity
            keyName = key[0].__name__ # We get the name from the class itself
            keyType = KEY_TYPE_NAMED_CLASS
            keyClass = key[0]
        
        # Enforce that referenced key is part of the current context        
        found = False
        for element in self.__class__.__dict__:                     
            if self.__class__.__dict__[element] == key:
                found = True
                    
        if not found:        
            raise Exception("Key [%s] is not found in the context %s" % (keyName, self))
        
        # Check to see if this key has already been initialized
        if not self.instances.get(keyName):
            
            try:
                args = key[2]
            except IndexError:
                args = {}
            
            # If entity is a sub-entity we need to pass an argument as the name
            if keyType == KEY_TYPE_GENERIC_CLASS:
                args['name'] = keyName
            
            self.instances[keyName] = keyClass(self, **args)
        
        return self.instances[keyName]
    
    def getParent(self):
        return self.parent
         
    def getClassName(self):
        return self.className              
                    
    def getName(self):
        
        return self.name      
                    
    def getCanonicalName(self, rootEntity=True, ancestorEntities=99, topLevel=True, recurse=False):
        """ Return a standard name for a hierarchy of entities 
        Recursive Call Order: Button -> Window -> Window -> Application
        
        @keyword name: For recursive calls to pass the child name 
        @keyword parents: Include parent entities
        
                                                                        # Notebook.FileMenu.SaveDialog,button    # Notebook.FileMenu.SaveDialog
        ancestorEntities=False                                          # Notebook.SaveDialog,button             # Notebook.SaveDialog
        ancestorEntities=False                                          # SaveDialog,button                      # .SaveDialog        
        rootEntity=False, ancestorEntities=False, parentEntity=False    # ,button                                # .SaveDialog
        """        
        
        # Use ,. as separator based on whether this is a sub-entity (owned by a window)
        if self.subEntity:
            prefix = ","
            name = self.name[:1].lower() + self.name[1:]            
        else:
            prefix = "."
            name = self.name
            
        # if there is no parent, then no prefix dot/comma needed
        if not self.parent: 
            prefix = ""
            
        if topLevel: # always show top level
            pass
        elif rootEntity and not self.parent: # if set to display rootEntity and root node 
            pass 
        elif not rootEntity and not self.parent: # if root entity and set not to display parent 
            name = "" 
            prefix = ""
        elif not ancestorEntities and self.parent: # if non-top level entity and set not to display parents (and is not a root node) 
            name = ""
            prefix = ""
        elif not recurse and not topLevel: # If this is first call and set to not display top level
            name = ""
            prefix = "" 
                
        # Recurse
        if self.parent:
            
            # If this is a family and familyEntites is an integer, count down
            ancestorEntities = ancestorEntities-1 if self.family and not isinstance(ancestorEntities, bool) and ancestorEntities else ancestorEntities              
            
            return self.parent.getCanonicalName(rootEntity=rootEntity, ancestorEntities=ancestorEntities, topLevel=False, recurse=True) + prefix + name
        else:
            return prefix + name;
            
         
    def __str__(self):
        
        return "%s:%s" % (self.getCanonicalName(), self.className)

        
    def formatPrefix(self, showBaseline=False, showStackTrace=True):
        """
        Used for logging functions to create line prefix which states the entity name, type and stack trace
        """        
                
        curframe = inspect.currentframe()
        calframes = inspect.getouterframes(curframe, 1)
                
        # form the stack trace, remove frames that are not entirely important to see in the logs        
        trace = ""
        if showStackTrace:
            for frame in calframes:
                print frame
               
                try:
                    match = re.search(r"[ =]([A-Z]\w+?)\(", frame[4][0]) # try and capture only new objects 
                    if match and match.group():                                        
                        trace = "->" + match.group(1) + trace 
                except TypeError:
                    pass
                       
    def isValid(self):
        """ Return the current status of the entity """
        return (self.status == self.STATUS_VALID)
    
    def invalidate(self, triggeredByEntity=None):
        """ Invalidate this entity (eg. Window has moved, or disappeared) """
                
        # Check to see if it is already invalid
        if self.status != self.STATUS_INVALID:
            self.status = self.STATUS_INVALID        
            self.logger.trace("invalidated by %s" % triggeredByEntity)
            
            # Reset instances
            self.instances = {}
        
        
        # Invalidate parents if state linked
        if self.statusCascade and self.parent:
            self.parent.invalidate(triggeredByEntity=triggeredByEntity)        
    
    def move(self, region):
        
        self.validate()        
        
        self.region.mouseMove(self.region)
        self.region.mouseDown(InputEvent.BUTTON1_MASK)
        self.region.mouseMove(region)
        self.region.mouseUp(InputEvent.BUTTON1_MASK)
        
        self.invalidate()
        
    def getRegionFinder(self):
        """
        For regionFinder to be valid, we need to validate first
        """
        
        return self.regionFinder
    
    def validate(self, timeout=None):
        
        parentRegion = None
        
        if self.status != self.STATUS_VALID:
            
            # make sure parents are valid too!
            if self.statusCascade:
                self.parent.validate()
            
            if self.parentRegion:
                parentRegion = self.parentRegion
            elif self.parent and self.parent.isValid(): # get parent region if we have a parent and it is valid
                parentRegion = self.parent.region
            
            # Allow for argument override
            timeout = timeout if timeout != None else self.timeout
                
            self.logger.trace("trying to validate, parentRegion=%%s timeout=%d" % self.timeout,  self.logger.getFormatter()(parentRegion))

            
            try: 
                
                self.regionFinder.setRegion(parentRegion)
                self.region = self.regionFinder.find(timeout=timeout)
                self.logger.debug('identified at %%s', self.logger.getFormatter()(self.region).showBaseline())                
                
                self.status = self.STATUS_VALID
            except ImageSearchExhausted, e:   
                raise UpdateFailureException("-- cannot find window")
            
        return self
        
    def getResult(self, **resultArgs):
        """
        This will initiate a resulting Entity.  Used by entities that have a visual result of interacting with itself.  
        """
        
        # Set args for proxy objects
        try:
            self.result.setResultArgs(resultArgs)
        except AttributeError, e:
            pass
        finally:
            pass        
        
        # Allow for the result to have a different context than just the parent           
        resultParent = self.resultParent if self.resultParent else self.parent
        resultParent = resultParent(self.parent) if inspect.isfunction(resultParent) else resultParent # Evaluate lambda resultParent       
        
        # Evalute Lambda's results
        result = self.result() if inspect.isfunction(self.result) else self.result
        
        # Is the result initiated already?
        if callable(result):
            
            try: # Try as a bound function
                return result.im_func(resultParent, caller=self, **resultArgs)
            except AttributeError: # im_func doesn't exist, not a bound method
                return result(resultParent, caller=self, **resultArgs)
        else:
            # Result has already be initialized
            return result

    def getRootEntity(self):
        """ 
        Will return the top most parent. (ie. The Entity that subclasses Application) 
        """

        if self.parent:
            return self.parent.getRootEntity()
        else:
            return self
        
    def getRegion(self):        
        self.validate()
        return self.region
    
    def getX(self):
        self.validate()
        return self.region.getX()
    
    def getY(self):
        self.validate()
        return self.region.getY()
        
    def getW(self):
        self.validate()
        return self.region.getW()
    
    def getH(self):
        self.validate()
        return self.region.getH()
    
    def focus(self):        
        self.validate()
        self.config.getScreen().mouseMove(self.region) 
        return self
    
    def assertThat(self, text):        
        self.validate()
        self.logger.info("Asserting [%s]" % text)
        
        baselinePath = self.config.imageBaseline + "/assert/" +  str(Env.getOS()).lower() + "/" + text + ".png"
        baseline = Pattern(baselinePath)
        
        # TODO: Refactor to allow for using RegionFinder class so PNG attributes can be used
        try:
            ImageLocator().locate( baselinePath )            
            result = self.region.find(baseline)                    
            self.logger.info('%%s matched %%s', self.logger.getFormatter()(result), self.logger.getFormatter()(baseline))
        except FindFailed, e:            
            self.logger.error('%%s does not match %%s', self.logger.getFormatter()(self.region), self.logger.getFormatter()(baseline))
            raise Exception("Assertion failure")        
        except FileNotFoundException, e: 
            # Baseline doesn't exist, save a copy
            shutil.copy(capture(self.region), baselinePath)        
            self.logger.error("Baseline not provided, please verify the baseline %s manually" % (baselinePath))    
                
    def findEntityByName(self, query):
        """
        Search for child entity definitions matching a particular query.
        """
        
        searcher = self.searcherStrategy()
        searcher.add(self.__class__)
        
        return self[searcher.search(query)['entity']]


    def waitUntilVanish(self, timeout=300, **resultArgs):
        """
        Detect once a entity has disappeared from the screen by continuously validating the object until it can no longer be validated.
        """
        
        tempTimeout = self.timeout # Set the timeout to shorter while we're using this method to see if it's dispapeared (possibly a bad idea: sideeffects on timeout)
            
        try:            
            self.validate(60)
            self.logger.trace("waiting until vanish")
            
            startTime = time.time()
            
            self.timeout = 1            
            
            # After we have validated it the first time, wait for it to disappear
            while True:
                
                # Enforce a maximum time to wait before timing out
                if (time.time() - startTime) > timeout:    
                    self.timeout = tempTimeout # set timeout back to its original value                
                    raise TookTooLongToVanishException()
                
                self.validate()
                self.invalidate()
                
        except FindExhaustedException, e:
            self.logger.info("vanished %%s", self.logger.getFormatter()(self.config.getScreen()))
            
        
        finally:
            self.timeout = tempTimeout # set timeout back to its original value
            
        return self.getResult(**resultArgs)
        
    def waitUntilAppears(self, timeout=60):
        """
        Detect when an entity appears on the screen by continuously trying to validate it.  Will give up after a certain period of time defined by 'timeout'
        """        
        
        startTime = time.time()
        tempTimeout = self.timeout # Set the timeout to shorter while we're using this method to see if it's dispapeared (possibly a bad idea: sideeffects on timeout)
        self.timeout = 1
        
        while True:
            
            try:
                self.validate()
                break
            except FindExhaustedException:
                pass
                
            # Enforce a maximum time to wait before timing out
            if (time.time() - startTime) > timeout:    
                self.timeout = tempTimeout # set timeout back to its original value                
                raise TookTooLongToAppearException()
            
        self.timeout = tempTimeout # set timeout back to its original value

    def mouseMove(self):
        """
        Move the mouse to the region of this entiy
        """
        
        self.validate()
        self.region.mouseMove(self.region)
        
        