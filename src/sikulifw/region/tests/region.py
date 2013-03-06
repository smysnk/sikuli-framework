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

import unittest

from sikuli import Region, Location

class RegionTests(unittest.TestCase):
    

    def setUp(self):
        #Region.debugPlaybackMode = True
        #Region.highlightTime = 2
        pass
    
    def tearDown(self):
        pass        
    
    def testSetOffset(self):
        
        region = Region(100,100,100,100)
        region = region.offset(Location(100,100))

        self.assertEqual(region.getX(), 200)
        self.assertEqual(region.getY(), 200)      
        self.assertEqual(region.getW(), 100)
        self.assertEqual(region.getH(), 100)      
        
    
    def testSetClickOffset(self):
        
        region = Region(100,100,100,100)
        region.setClickOffset(Location(10,10))
        
        # Check that it is set right
        location = region.getClickOffset()        
        self.assertEqual(location.getX(), 10)
        self.assertEqual(location.getY(), 10)
        
        location = region.getClickLocation()
        self.assertEqual(location.getX(), 160.0)
        self.assertEqual(location.getY(), 160.0)
        
    
    def testRegionCanAddRegion(self):      
        
        region = Region(100,100,100,100)
        region = region.add(Region(100,100,200,200))
        
        # Width/Height should have changed to 200/200
        self.assertEqual(region.getX(), 100)
        self.assertEqual(region.getY(), 100)
        self.assertEqual(region.getW(), 200)
        self.assertEqual(region.getH(), 200)
        
    def testCreateRegionFromList(self):      
        
        regions = [Region(50,50,50,50), Region(200,50,50,50), Region(200,50,50,50), Region(200,200,50,50)] 
        
        region = Region(regions)
        
        # Width/Height should have changed to 200/200
        self.assertEqual(region.getX(), 50)
        self.assertEqual(region.getY(), 50)
        self.assertEqual(region.getW(), 200)
        self.assertEqual(region.getH(), 200)

    def testCanLimitRegion(self):
        
        region = Region(50,50,400,400).limit( Region(150,100,150,25) )
        self.assertEqual(region.getX(), 150)
        self.assertEqual(region.getY(), 100)
        self.assertEqual(region.getW(), 150)
        self.assertEqual(region.getH(), 25)
        
        region = Region(100,100,200,200).limit( Region(50,50,400,400) )
        self.assertEqual(region.getX(), 100)
        self.assertEqual(region.getY(), 100)
        self.assertEqual(region.getW(), 200)
        self.assertEqual(region.getH(), 200)
        

    def testCanAddLocationToRegion(self):
        
        region = Region(100,100,1,1)
        
        # Check that initialized properly
        self.assertEqual(region.getX(), 100)
        self.assertEqual(region.getY(), 100)
        self.assertEqual(region.getW(), 1)
        self.assertEqual(region.getH(), 1)

        region = region.add(Location(50,50))
        
        # X,Y Should have changed to 50
        self.assertEqual(region.getX(), 50)
        self.assertEqual(region.getY(), 50)
        
        # W,H should have changed to 50
        self.assertEqual(region.getW(), 51)
        self.assertEqual(region.getH(), 51)
        
        region = region.add(Location(200,50))

        # Width/Height should have changed to 200/200
        self.assertEqual(region.getX(), 50)
        self.assertEqual(region.getY(), 50)
        self.assertEqual(region.getW(), 150)
        self.assertEqual(region.getH(), 51)
        
        
        region = region.add(Location(200,200))
        
        # Width/Height should have changed to 200/200
        self.assertEqual(region.getX(), 50)
        self.assertEqual(region.getY(), 50)
        self.assertEqual(region.getW(), 150)
        self.assertEqual(region.getH(), 150)
        
        
        
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()