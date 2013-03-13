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

import os
from org.sikuli.script import Region
from sikuli.Sikuli import capture
import re
from org.sikuli.script import Location, Pattern, Match
from sikuli.Screen import Screen
import entity
from region.finder import FinderAbstract

class LabelCouldNotBeDeterminedException(Exception):
    pass

class Formatter(object):
    
    entity = None
    label = None
    doShowBaselines = False
    items = None
    series = None
    state = None
    level = None
    
    tool = None
    config = None
    
    @classmethod
    def setDefaultLevel(cls, level):
        cls.level = level
    
    @classmethod
    def setTool(cls, tool):
        cls.tool = tool
        
    @classmethod
    def setConfig(cls, config):
        cls.config = config
    
    def __init__(self, entity, name=None):
        
        
        if isinstance(entity, str):
            self.setLabel(entity)
            
        elif isinstance(entity, list):            
            self.addBaselines(name, entity)
        
        else:
            self.entity = entity
        

    def __str__(self):
        
        labelStr = ""
        
        if self.label:
            labelStr = '"%s"' % self.label
        
        elif isinstance(self.entity, Match):
            match = re.search(r"(?P<match>Match.*?\])", str(self.entity), re.IGNORECASE)
            if match:
                labelStr = '"%s"' % match.group("match")
            else:
                raise Exception("Unable to regex match on [%s]" % str(self.entity))            
        
        elif isinstance(self.entity, Screen):
            match = re.search(r"(?P<screen>Screen.*?\])", str(self.entity), re.IGNORECASE)
            if match:
                labelStr = '"%s"' % match.group("screen")
            else:
                raise Exception("Unable to regex match on Screen")            
        
        elif isinstance(self.entity, Region):
            match = re.search(r"(?P<region>(Region).*?)@(?P<screen>Screen.*\])", str(self.entity), re.IGNORECASE)
            if match:
                labelStr = '"%s"' % match.group("region")
            else:
                raise Exception("Unable to regex match on [%s]" % str(self.entity))

        elif isinstance(self.entity, Pattern):
            labelStr = '"%s"' % str(self.entity)                        
            
        else:
            labelStr = '%s' % str(self.entity)
        
        ## Create Suffix
        images = [] 
        regionFinder = None
        region = None
        
        if not self.meetsLogThreshold():
            pass # Don't log this image, doesn't meet logging threshold
        
        elif isinstance(self.entity, entity.Entity):
            # If entity has a valid regions
            if self.entity.region:
                region = self.entity.region
            
            # Get the enity names from regionFinder
            regionFinder = self.entity.getRegionFinder()
                    
        elif isinstance(self.entity, FinderAbstract):
            region = self.entity.getLastRegionFound()
            regionFinder = self.entity
            
        elif isinstance(self.entity, Region):
            region = self.entity
            
        elif isinstance(self.entity, Pattern):
            
            match = re.search(r'Pattern\("(?P<path>.*?)"\)', str(self.entity), re.IGNORECASE)
            if match:
                imagePath = match.group("path")
                images.append(self.tool.saveAsset(imagePath))
            else:
                raise Exception("Unaable to match path")

                # Capture images
        if self.meetsLogThreshold() and region:
            images.append(self.tool.saveAsset((capture(region))) + ':Actual')
        
        if self.meetsLogThreshold() and regionFinder and self.doShowBaselines:
            seriesRange = []
            if self.series != None:
                seriesRange.append(self.series)
            elif regionFinder.getLastSeriesMatched() != None:
                seriesRange.append(regionFinder.getLastSeriesMatched())
            elif regionFinder.getSeriesRange():
                seriesRange = regionFinder.getSeriesRange()
             
            state = self.state if self.state else regionFinder.getState()
                        
            for series in seriesRange:
                for image in regionFinder.getImageNames(series=series, state=state):
                    #images.append(image + ':Baseline')
                    #images.append(self.tools.saveAsset(image) + ":%s" % os.path.basename(image))
                    images.append(self.tool.saveAsset(image) + ":%s" % 'series_' + str(series))
        
        imageStr = ','.join(images)  
    
        return '[%s](%s)' % (labelStr, imageStr)
    
    def meetsLogThreshold(self):
        
        return self.level >= self.config.getScreenshotLoggingLevel()
        
    
    def setLogLevel(self, level):        
        self.level = level  
        return self      
    
    def setLabel(self, label):
        
        self.label = label         
        return self
        
    def showBaseline(self, show=True, series=None, state=None):
        
        self.doShowBaselines = show
        self.series = series
        self.state = state
        return self
    
    def setSeries(self, series):
        self.series = series
        return self
    
    def setState(self, state):
        self.state = state
        return self
    
        
    def add(self, key, item):
        
        if isinstance(item, list) or isinstance(item, key):
            self.items[key] = item
        else: 
            raise Exception("Unsupported item")
        

        