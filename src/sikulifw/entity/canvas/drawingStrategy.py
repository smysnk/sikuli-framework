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

from org.sikuli.script import Location
from sikuli.Region import Region

class DrawingStrategy(object):
    
    obj = None
    enabled = None
    
    def __init__(self, obj):
        
        self.obj = obj
        self.state = False
        
    def goto(self, x, y):
                        
        raise Exception("This method must be subclased")

    def on(self):
        self.enabled = True
        
    def off(self):
        self.enabled = False


class ContiniousDrawingStrategy(DrawingStrategy):
    
    queue = None
    region = None
    
    def goto(self, x, y):
        
        
        if self.enabled:
            self.queue.append([x, y])
            
            if not self.region:
                self.region = Region(x, y, 1, 1)
            else:
                self.region = self.region.add(Location(x, y))
                   
            
    def on(self):
        
        super(ContiniousDrawingStrategy, self).on()        
        self.queue = []
        self.region = None
    
    def off(self):

        super(ContiniousDrawingStrategy, self).off()
        
        # Prepare to draw annotation
        self.obj.center(self.region)
        
        # Move to first location
        self.obj.mouseMove(self.queue[0][0], self.queue[0][1])        
        self.obj.startDrawing()

        for location in self.queue[1:]:
            self.obj.mouseMove(location[0], location[1])
        
        self.obj.stopDrawing()

        

class SegmentDrawingStrategy(DrawingStrategy):
    
    x = None
    y = None
    
    def goto(self, x, y):

 
        if self.enabled and self.x != None and self.y != None:
            
            # Make sure the canvas area is setup right
            self.obj.center(Location(float(self.x), float(self.y)))
            self.obj.center(Location(float(x), float(y)))
            
            # Draw a line from the last location
            self.obj.mouseMove(float(self.x), float(self.y))
            self.obj.startDrawing()
            self.obj.mouseMove(float(x), float(y))
            self.obj.stopDrawing()

        
        self.x = x
        self.y = y        


class PracticeDrawingStrategy(DrawingStrategy):
    
    region = None
    
    def goto(self, x, y):
        
        if not self.region:
            self.region = Region(x, y, 1, 1)
        else:
            self.region = self.region.add(Location(x,y))
        
    def on(self):
        
        self.region = None        
        super(PracticeDrawingStrategy, self).on()
        
    def off(self):
        
        self.obj.center(self.region)
        super(PracticeDrawingStrategy, self).off()
    
    