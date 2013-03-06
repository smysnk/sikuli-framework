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

from org.sikuli.script import Location, Pattern
import types
from sikuli import Env, Region
from org.sikuli.script import Region as JRegion
from org.sikuli.script import Env as JEnv
#from sikulifw.config import Config
#from sikulifw.logger import Logger
from sikuli.Sikuli import capture

# =============================================== #
#          Overwritten sikuli methods             #
# =============================================== #

# function for calling native sikuli methods
def sikuli_method(name, *args, **kwargs):
    return sys.modules['sikuli.Sikuli'].__dict__[name](*args, **kwargs)

# overwritten Screen.exists method
def exists(target, timeout=None):
    addFoundImage(getFilename(target))
    return sikuli_method('exists', target, timeout)

# =============================================== #
#          Overwritten sikuli classes             #
# =============================================== #        

@staticmethod
def EnvGetOSVersion(fullName=None):
    if not fullName:
        return Env.oldGetOSVersion();
    elif Env.oldGetOSVersion() == '5.1':
        return 'XP'
    elif Env.oldGetOSVersion() == '6.0':
        return 'Vista'
    elif Env.oldGetOSVersion() == '6.1':
        return 'Win7'

Env.oldGetOSVersion = Env.getOSVersion
Env.getOSVersion = EnvGetOSVersion

## Java Region patching
def add(self, operand):
    
    # If we're trying to add None, just return the original region
    if not operand:
        return self
    
    regions = [self, operand]
    
    # more than one region, get min/max region        
    minX, minY = 9999, 9999 
    maxX, maxY = -9999, -9999
    for region in regions:
        if region.getX() < minX: minX = int(region.getX())  
        if region.getY() < minY: minY = int(region.getY())
        
        # If this is a region type
        if hasattr(region, "getW") and hasattr(region, "getH"):  
            if (region.getX() + region.getW()) > maxX: maxX = region.getX() + region.getW()  
            if (region.getY() + region.getH()) > maxY: maxY = region.getY() + region.getH()
        else:
            if region.getX() > maxX: maxX = int(region.getX())
            if region.getY() > maxY: maxY = int(region.getY())
    
    return Region(minX, minY, maxX-minX, maxY-minY)

JRegion.add = add

# Java Region patching
def limit(self, operand):
    
    # If we're trying to limit None, return original
    if not operand:
        return self
    
    x1 = self.getX() if self.getX() > operand.getX() else operand.getX()
    y1 = self.getY() if self.getY() > operand.getY() else operand.getY()
    x2 = (self.getX() + self.getW()) if (self.getX() + self.getW()) < (operand.getX() + operand.getW()) else (operand.getX() + operand.getW())
    y2 = (self.getY() + self.getH()) if (self.getY() + self.getH()) < (operand.getY() + operand.getH()) else (operand.getY() + operand.getH())
    
    # Check region is valid positive 
    if x2-x1 < 0 or y2-y1 < 0:
        raise Exception("Region %s is outside the bounds of the ParentRegion %s" % (self, operand))
        
    
    return Region(x1, y1, x2-x1, y2-y1)    

JRegion.limit = limit

def offset(self, operand):
    
    self.setX(self.getX() + operand.getX())
    self.setY(self.getY() + operand.getY())
    
    return self    

##
def regionInit(self, operand, *args, **kargs):
    
    # Handle a list of regions        
    if isinstance(operand, list):
        
        region = None
        
        for item in operand:
            
            if region:
                region = region.add(item)
            else:
                region = item
                
        self.oldInit(region, *args, **kargs)
    
    else:
        self.oldInit(operand, *args, **kargs)

JRegion.oldInit = JRegion.__init__
JRegion.__init__ = regionInit


## Region patching
#JRegion.timeout = Config.regionTimeout
JRegion.clickOffset = Location(0,0)

# Define setClickOffset
def setClickOffset(self, offset):
        
    assert isinstance(offset, Location)    
    self.clickOffset = offset
    
JRegion.setClickOffset = setClickOffset

# Define getClickLocation
def getClickLocation(self):
    
    x = self.x + (self.w/2) + self.clickOffset.getX()
    y = self.y + (self.h/2) + self.clickOffset.getY()
    
    return Location(x, y)

JRegion.getClickLocation = getClickLocation


# Define getClickLocation
def getClickOffset(self):
    
    return self.clickOffset

JRegion.getClickOffset = getClickOffset

