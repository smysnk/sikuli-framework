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

from org.sikuli.script import ImageLocator, FindFailed, Pattern
from java.io import FileNotFoundException
import time
from sikuli.Region import Region
from sikulifw.region.exception import ImageMissingException,\
    ImageSearchExhausted, FindExhaustedException
import sys
import os
import re

class FinderAbstract(object):
    """
    Abstract class for RegionFinder like finders to support unit testing
    """    
    pass


class Finder(FinderAbstract):
    """ 
    This is the main class used to find baselines on the screen.  It supports a number of features to allow for baselines to be 
    matched in a more precise fashion.  It is like a visual regular expression engine.
    
    -- single: single representation of the menu (for static menus)
    images/App.Menu.png

    -- single, multi-image: segmented (for dynamic menus: changes as resized)
    images/App.Menu-0.png
    images/App.Menu-1.png
    
    -- set: for menus that can exist in different orientations
    images/App.Menu[0].png
    images/App.Menu[1].png
    
    -- set, multi-image: different orientations, segmented (changes as resized) 
    images/App.Menu[0]-0.png
    images/App.Menu[0]-1.png
    images/App.Menu[1]-0.png
    images/App.Menu[1]-1.png
    
    """        
    
    # collection constants
    COL_TYPE_SINGLE = 'SINGLE'
    COL_TYPE_SERIES = 'SERIES'
    COL_TYPE_SEQUENCE = 'SEQUNECE'
    COL_TYPE_SERIES_SEQUENCE = 'SERIES_SEQUENCE'

    # name types
    NAME_TYPE_FULL = 'FULL'                     # Notebook.FileMenu.SaveDialog,button
    NAME_TYPE_GENERIC = 'GENERIC'               # Notebook.SaveDialog,button    
    NAME_TYPE_CLASS_ENTITY = "CLASS_ENTITY"     # Button,button
    NAME_TYPE_CLASS = 'CLASS'                   # Button
        
    transform = None
    config = None
    
    logger = None
    name = None
    collectionType = None
    nameType = None
    seriesRange = None
    entity = None
    region = None
    state = None    
    lastRegionFound = None   # Last region found using the find() method
    lastSeriesFound = None  # Last series found using the find() method
    
    filename = None
    path = None
    
    threadLock = None
    
    @classmethod
    def setLogger(cls, logger):
        cls.logger = logger
        
    @classmethod
    def setConfig(cls, config):
        cls.config = config
        
    @classmethod
    def setTransform(cls, transform):
        cls.transform = transform
    
    def __init__(self, entity, region=None, state=None):
        
        super(Finder, self).__init__()
        
        self.logger = self.__class__.logger(self) 
        self.entity = entity # entity images are associated with        
        self.setRegion(region)
        
        # check button state
        if state == None or state == "":
            self.state = "" #enabled state doesn't need a tag
        else:
            self.state = "[%s]" % state        
        
        """
        NAME_TYPE_FULL = 'FULL'                     # App.FileMenu.SaveDialog,button         # App.FileMenu.SaveDialog
        NAME_TYPE_GENERIC = 'GENERIC'               # App.SaveDialog,button                  # App.SaveDialog
        NAME_TYPE_CLASS_ENTITY = 'CLASS_ENTITY'     # Button,button                          # Window.SaveDialog
        NAME_TYPE_CLASS = 'CLASS'                   # Button                                 # Window
        """
        
    
    def findBaselines(self):
        
        # If this is set we've already found stuff       
        if self.collectionType: return
        
        for filename, nameType in ( \
                (self.entity.getCanonicalName(ancestorEntities=False, topLevel=False) + '/' + self.entity.getCanonicalName(),self.NAME_TYPE_FULL), \
                (self.entity.getCanonicalName(ancestorEntities=False, topLevel=False) + '/' + self.entity.getCanonicalName(ancestorEntities=1), self.NAME_TYPE_GENERIC), \
                (self.entity.getCanonicalName(ancestorEntities=False, topLevel=False) + '/' + self.entity.getClassName() + self.entity.getCanonicalName(rootEntity=False, ancestorEntities=False), self.NAME_TYPE_CLASS_ENTITY), \
                (self.entity.getCanonicalName(ancestorEntities=False, topLevel=False) + '/' + self.entity.getClassName(), self.NAME_TYPE_CLASS), \
                (self.entity.getClassName() + self.entity.getCanonicalName(rootEntity=False, ancestorEntities=False), self.NAME_TYPE_CLASS_ENTITY), \
                (self.entity.getClassName(), self.NAME_TYPE_CLASS)
            ):
        
            # single 
            try:
                self.path = ImageLocator().locate(filename + self.state + self.config.imageSuffix)[:-4] + ".png" # get full path, minus .png extension
            except:
                pass # file doesn't exist
            else:       
                self.filename = filename     
                self.nameType = nameType
                self.collectionType = self.COL_TYPE_SINGLE
                self.seriesRange = [0,]
                self.__logFound()
                return 
                
            # sequence 
            try:
                self.path = ImageLocator().locate(filename + '-0' + self.state +  self.config.imageSuffix)[:-4] + ".png" # get full path, minus .png extension
            except:
                pass # file doesn't exist
            else:             
                self.filename = filename
                self.nameType = nameType
                self.collectionType = self.COL_TYPE_SEQUENCE
                self.seriesRange = [0,]
                self.__logFound()  
                return
    
            # series
            seq = 0
            while True:
                try:                
                    self.path = ImageLocator().locate(filename + '[' + str(seq) + ']' + self.state + self.config.imageSuffix)[:-4] + ".png" # get full path, minus .png extension               
                except:
                    break # end of series
                else:
                    seq += 1
    
            if seq > 0:
                self.filename = filename
                self.nameType = nameType
                self.collectionType = self.COL_TYPE_SERIES
                self.seriesRange = range(0, seq)
                self.__logFound()                
                return 
            
            # sequence + series
            seq = 0
            while True:        
                try:
                    self.path = ImageLocator().locate(filename + '[' + str(seq) + ']-0' + self.state + self.config.imageSuffix)[:-4] + ".png" # get full path, minus .png extension
                except:
                    break # end of sequence
                else:
                    seq += 1
                    
            if seq > 0: 
                self.filename = filename
                self.nameType = nameType
                self.collectionType = self.COL_TYPE_SERIES_SEQUENCE
                self.seriesRange = range(0, seq)                
                self.__logFound()
                return
            
            self.logger.trace("failed to find image on disk [\"%s%s\"] nameType=%s" % (filename, self.state, nameType))
                       
        raise ImageMissingException("cannot find image on disk [\"%s%s\"]" % (filename, self.state)) # if we don't have single image or sequence, file cannot be found
    
    def setRegion(self, region):

        if region:
            self.region = region # set the region to search within
        else:
            self.region = self.config.screen # default to entire screen
        
    
    def __logFound(self):       
        self.findBaselines()
        self.logger.trace("%%s colType=%s nameType=%s" % (self.collectionType, self.nameType), self.logger.getFormatter()(self).setLabel("Baselines"))
        
    def getImageNames(self, series=0, state=None):
        """ Return the image names for a certain sequence 
        @keyword type: Collection type
        @keyword series: If COL_SERIES or COL_SERIES_SEQUENCE, series # 
        
        """
        
        # Populate path & collectionType
        self.findBaselines()
                       
        files = []
        sequence = 0 
        while True:            
            try:        
                # form suffix based on type, series/sequence #        
                if self.collectionType == self.COL_TYPE_SINGLE:
                    suffix = ''
                elif self.collectionType == self.COL_TYPE_SERIES:
                    suffix = '[' + str(series) + ']'
                elif self.collectionType == self.COL_TYPE_SEQUENCE:
                    suffix = '-' + str(sequence)
                elif self.collectionType == self.COL_TYPE_SERIES_SEQUENCE:
                    suffix = '[' + str(series) + ']-' + str(sequence)
                
                # Create the path to the images
                match = re.search(r"([^/\\[]*.?)(?:|-[0-9]{1,2}|\[[0-9]{1,2}\]|\[[0-9]{1,2}\]-[0-9]{1,2}).png", self.path, re.IGNORECASE)
                
                filename = os.path.dirname(self.path) + "/" + match.group(1) + suffix + ".png"            
                files.append( filename )
                
            except FileNotFoundException, e:
                break # end of sequence
            
            else:
                # If single image, or series only 1 file to return
                if (self.collectionType == self.COL_TYPE_SINGLE) or (self.collectionType == self.COL_TYPE_SERIES): 
                    return files
                else:
                    sequence += 1
        
        assert len(files) > 0 # we should have returned at least one file        
        return files
    
    def getEntity(self):
        return self.entity
    
    def getLastRegionFound(self):
        return self.lastRegionFound
    
    def getLastSeriesMatched(self):
        return self.lastSeriesFound
    
    def getSeriesRange(self):
        self.findBaselines()
        return self.seriesRange
    
    def find(self, timeout=5):
        """
        Will attempt over a period of time to find the baseline images on the screen.
        """
        
        self.findBaselines()
        
        self.logger.trace(" colType=%s" % (self.collectionType))
        
        startTime = time.time() 
        
        attempt = 0
        while (time.time() - startTime) < timeout:
            try:            
                result = self.performFind()
                self.logger.trace("-- success! [attempt=%i]" % attempt)                
                return result
            except ImageSearchExhausted, e:  
                self.logger.trace("-- failure! [attempt=%i]" % attempt)
            attempt += 1
                
        raise FindExhaustedException("entity=%s timeout=%ds elapsed=%ds attempts=%d" % (self.entity, timeout, (time.time() - startTime), attempt))
                                   
 
    
    def performFind(self):
        """
        Loads the baseline images from disk and finds them on the screen.  
        Works with the Transforms class to load extra data stored in the PNG's to control how they're matched.
        """
        
        # sequence and series                
        for series in self.seriesRange:            
            regions = []
            lastRegion = self.region
            nextRegion = Region(self.region)
            
            # try to match all images in the sequence       
            try:                                
                for (sequence, filename) in enumerate(self.getImageNames(series=series,state=self.state)):
                    
                    transform = self.transform(filename, entity=self.entity, regionsMatched=regions, context=self)     
                    
                    # Apply prev search attribs
                    nextRegion = transform.apply(nextRegion, self.transform.CONTEXT_PREVIOUS)
                    # Apply search attribs
                    
                    pattern = transform.apply(Pattern(filename), self.transform.CONTEXT_CURRENT)
                    self.logger.trace("Loading %%s", self.logger.getFormatter()(pattern))            
                    
                    # find the image on the screen
                    lastRegion = nextRegion.wait( pattern ) # If we don't set to zero wait time (dialog handler threads wait indefinitely)
                    lastRegion = transform.apply(lastRegion, self.transform.CONTEXT_MATCH)
                    
                    self.logger.trace("validated %%s %%s in region %%s nameType=%s colType=%s ser=%s seq=%s" % (self.nameType, self.collectionType, series, sequence), self.logger.getFormatter()(pattern), self.logger.getFormatter()(lastRegion), self.logger.getFormatter()(nextRegion))
                    regions.append( lastRegion ) 

                    # Transform next region with the spacial region
                    # spacialRegion is only used if there are spacial modifiers
                    nextRegion = transform.apply(Region(nextRegion), self.transform.CONTEXT_NEXT, override=lastRegion)

            except FindFailed, e:
                self.logger.trace("failed to find on screen %%s in %%s nameType=%s colType=%s ser=%s seq=%s" % (self.nameType, self.collectionType, series, sequence),  self.logger.getFormatter()(self).setLabel("Images"), self.logger.getFormatter()(nextRegion))
            else:
                
                region = Region(regions)
                region = transform.apply(region, self.transform.CONTEXT_FINAL)
                
                # Apply entity transforms
                transform.apply(self.entity, self.transform.CONTEXT_ENTITY)
                
                self.lastRegionFound = region
                self.lastSeriesFound = series
                return region
        
        raise ImageSearchExhausted()
    
    def __str__(self):        
        if self.entity:
            return str(self.entity) + "->%s" % (self.__class__.__name__)
        else:
            return self.__class__.__name__    

    def getState(self):
        return self.state