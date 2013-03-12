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

from sikuli.Region import Region
from sikulifw.region.finder import FinderAbstract

class Finder(FinderAbstract):
    
    baselines = None
    callbacks = []
    test = None
    state = None
    
    def __init__(self, entity, region=None, state=None, *args, **kwargs):
        object.__init__(self, *args, **kwargs)
        
        # If we have any callbacks setup, run them!
        if len(self.callbacks) > 0:
            self.callbacks.pop(0)(self.test, entity=entity, *args, **kwargs)
            
        self.baselines = {}
        self.state = state
    
    @classmethod
    def setTest(cls, test):
        cls.test = test
    
    @classmethod
    def addCallback(cls, callback):
        cls.callbacks.append(callback)
    
    def find(self, timeout=0):
        return Region(0,0,100,100)

    def getImageNames(self, series=0, state=None, md5=False):
        
        state = "[" + state + "]" if isinstance(state, str) else ""
        
        try:
            baselines = []        
            for baseline in self.baselines[series]:
                
                if md5:
                    baselines.append('MD5HASH.png')
                else:
                    baselines.append(baseline + '%s.png' % state)
        except KeyError:
            pass # No baseline images for this series
        
        return baselines
    
    def getLastRegionFound(self):
        return Region(0,0,100,100)
    
    def addBaseline(self, name, series=0):
        
        try:
            self.baselines[series].append(name)
        except KeyError:
            self.baselines[series] = []
            self.baselines[series].append(name)
    
    def getState(self):
        return self.state
    
    def getLastSeriesMatched(self):
        return 0
    
    def getLastRegionMatched(self):
        return Region(0,0,100,100)
        
    def setRegion(self, region):
        return self
    
    def __str__(self):
        return "RegionFinderMock"
        
        
        
        