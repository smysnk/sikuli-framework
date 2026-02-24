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

from org.sikuli.basics import OS
from org.sikuli.script import KeyModifier, Key, Location
import re

from region.exception import FindExhaustedException
from entity.exception import StateFailedException
from sikuli.Sikuli import sleep
from sikuli.Region import Region
import time
from entity.entity import Entity

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
        except FindExhaustedException:
            raise StateFailedException("incorrect state [%s]" % state)
        else:
            self.logger.info("completed successfully!")
                               
        return self.getResult(**resultArgs)
    
    def __changed(self, event):
        
        # Progress bar has changed        
        self.lastChange = time.time()
        
