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

from org.sikuli.script import Location, Region
import math

class TurtleFoodComponent(object):
    
    def getRegion(self):
        
        return None
    
    def digest(self, turtle):
        
        print "I am being digested by %s" % turtle
        
        
class TurtleFoodComposite(TurtleFoodComponent):
    
    food = None
    
    def __init__(self):
        
        self.food = []
    
    def add(self, component):
        
        self.food.append(component)
    
    def remove(self, component):
        
        self.food.remove(component)
        
    def getRegion(self):
        
        # Get the region of the food to digest in this group
        region = None
        for food in self.food:
            if region:
                region = region.add(food.getRegion())
            else:
                region = food.getRegion()
                
        return region

class On(TurtleFoodComponent):

    def digest(self, digestor):
        
        digestor.on()
        
class Off(TurtleFoodComponent):
    
    def digest(self, digestor):
        
        digestor.off()
        
class Point(TurtleFoodComponent):
    
    x = None
    y = None
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def digest(self, digestor):
        
        digestor.goto(self.x, self.y)
        
    def getRegion(self):
        
        return Region(self.x, self.y, 1, 1)
            
        
class Line(TurtleFoodComponent):
    
    x1 = None
    y1 = None
    x2 = None
    y2 = None
    
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
                      
    def digest(self, digestor):
        
        digestor.goto(self.x1, self.y1)
        digestor.goto(self.x2, self.y2)        
        
    def getRegion(self):
        
        return Region(self.x1, self.y1, 1, 1).add(Location(self.x2, self.y2))
            
           
class Circle(TurtleFoodComponent):
    
    resolution = 50
    size = 10
    
    def __init__(self, size, resolution):
        self.size = size
        self.resolution = resolution
    
    def digest(self, turtle):
        #TurtleFood.digest(self, stomach)
        
        resolution = self.resolution / 100.0
        print resolution
        step = 1 / resolution 
        
        turtle.on()
        for i in range(0, (360/step)):
                        
            turtle.right(step)
            turtle.forward(self.size)
            
        turtle.off()
        
class FoodGroup(TurtleFoodComposite):
    
    x = 0
    y = 0
    digestor = None
    
    def digest(self, digestor):
        
        self.digestor = digestor
        
        for food in self.food:
            food.digest(self)
        
        # Reset coords
        self.x = 0
        self.y = 0
            
    def goto(self, x, y):
        
        dx = x - self.x 
        dy = y - self.y 
        
        # Translate into move commands
        self.digestor.move(dx, dy)
        
        self.x += dx
        self.y += dy
        
    def on(self):
        
        self.digestor.on()
        
    def off(self):
        
        self.digestor.off()
        
        

class FoodPlatter(TurtleFoodComposite):
    
    
    digestor = None
    
    def digest(self, digestor):
        
        self.digestor = digestor

        # Digest ALL THE FOOD!!        
        for food in self.food:
            food.digest(digestor)
    
    def move(self, x, y):
        
        self.digestor.move(x,y)
    
    def on(self):
        
        self.digestor.on()
        
    def off(self):
        
        self.digestor.off()
            

class Turtle(object):
    
    # Entities
    canvas = None
    scrollBar = None    
    
    log = None
    facing = None
    x = None
    y = None
    
    homeX = None
    homeY = None
    
    logger = None

    def __init__(self, canvas):
        
        self.canvas = canvas.validate()

        self.facing = 90.0
        self.x = int(self.canvas.getW() / 2)
        self.y = int(self.canvas.getH() / 2)
        self.homeX = self.x
        self.homeY = self.y
        self.logger = None
        self.enabled = True
        
    def home(self):
        
        self.facing = 90.0
        self.canvas.goto(self.homeX, self.homeY)
        
        return self
        
    def goto(self, x, y):
        
        self.canvas.goto(x, y)
        
        self.x = x
        self.y = y
        
        return self
        
    def move(self, x, y):
 
        self.x += x
        self.y += y
                
        self.canvas.goto(self.x, self.y)
         
        return self

        
    def forward(self, distance):
        
        y = -math.sin(math.radians(self.facing)) * distance # Soh, reverse Y because we're using screen coords vs cartesian
        x = math.cos(math.radians(self.facing)) * distance # Cah
        #self.log.info("move forward x=%d y=%d (facing=%d, dist=%d)" % (x, y, self.facing, distance)) 
        
        self.move(x, y)
        
        return self
            
    def backwards(self, distance):
        
        y = -math.sin(math.radians(self.facing)) * distance # Soh
        x = math.cos(math.radians(self.facing)) * distance # Cah 
        #self.log.info("move backwards x=%d y=%d (facing=%d, dist=%d)" % (x, y, self.facing, hyp))
        
        self.move(-x, -y)
                
        return self
        
    def left(self, degrees):
        
        self.facing += degrees
        
        #self.log.info("turning left deg=%d to %d" % (degrees, self.facing))
        
        return self
        
    def right(self, degrees):
          
        self.facing -= degrees
        
        #self.log.info("turning right deg=%d to %d" % (degrees, self.facing))
        
        return self
    
    def on(self):
        
        self.canvas.on()

        return self
    
    def off(self):
        
        self.canvas.off()

        return self
        
    def eat(self, food):        
        
        return food.digest(self) # Pass in who is digesting this food
                    
    def getX(self):
        
        return self.x
    
    def getY(self):
        
        return self.y
            
            