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

import unittest

from sikulifw.log import Logger
from sikulifw.region.transform import *

Logger.setRobotLogger(RobotLogger())
Logger.setFormatter(Formatter)


class Test(object):            
    region = None
    parent = None
    
    def __init__(self, region=None, parent=None):
        self.parent = parent            
        self.region = region
        
class Formatter(object):
    
    def setLogLevel(self, *args, **kargs):
        pass


class TransformsTests(unittest.TestCase):
    
    contexts = [Transform.CONTEXT_PREVIOUS, Transform.CONTEXT_CURRENT, Transform.CONTEXT_NEXT, Transform.CONTEXT_FINAL]         

    def setUp(self):
        Transform.setLogger(Logger)        

    def tearDown(self):
        pass        

    def testScreenNotTransformedSpacially(self):      
        
        screen = Screen(0)      
        transform = Transform({ \
                Transform.CONTEXT_PREVIOUS: [ \
                    RegionAbove(), \
                    RegionBelow(), \
                    RegionRight(), \
                    RegionLeft(), \
                    RegionNearby() \
                                              ], \
                Transform.CONTEXT_CURRENT: [ \
                                             ], \
                Transform.CONTEXT_NEXT: [ \
                    RegionAbove(), \
                    RegionBelow(), \
                    RegionRight(), \
                    RegionLeft(), \
                    RegionNearby() \
                                          ] \
              })
                
        for context in self.contexts:
            # Assert the screen is not transformed by a spacial attrib
            self.assertEqual(screen, transform.apply(screen, context))
        

    def testRegionOverrides(self):        
        """ Test that spacial override is applied """
        
        override = Region(500,500,100,100)
        screen = Screen(0)
        
        transform = Transform({ \
                Transform.CONTEXT_PREVIOUS: [], \
                Transform.CONTEXT_CURRENT: [], \
                Transform.CONTEXT_NEXT: [ \
                    RegionAbove(50), \
                                          ], \
                Transform.CONTEXT_FINAL: [] \
              })   
             
        for context in self.contexts:

            result = transform.apply(screen, context, override=override)
                         
            if context == Transform.CONTEXT_NEXT: 
                # Assert that override has taken place, and spacial attributes have been applied
                self.assertNotEqual(result, screen) 
                self.assertNotEqual(result, override)  
                self.assertEqual(result.getX(), 500)  
                self.assertEqual(result.getY(), 450)   
                self.assertEqual(result.getW(), 100) 
                self.assertEqual(result.getH(), 50) 
            
            else: # Result should be unchanged since context is different                
                self.assertEqual(result, screen)        
        
         
    def testSpacialAboveWithProximiterAppliedToContextOnly(self):
        """ Test spacial attributes are applied to context only """

        #print type, region, attrib.transform(region, type)        
        
        region = Region(500,500,100,100)
        transform = Transform({ \
                Transform.CONTEXT_PREVIOUS: [], \
                Transform.CONTEXT_CURRENT: [], \
                Transform.CONTEXT_NEXT: [ \
                    RegionAbove(50), \
                                          ] \
              })   

        for context in self.contexts:

            result = transform.apply(region, context)
                         
            if context == Transform.CONTEXT_NEXT: # Result should change since this is the context
                self.assertEqual(result.getX(), 500)
                self.assertEqual(result.getY(), 450)
                self.assertEqual(result.getW(), 100)
                self.assertEqual(result.getH(), 50)
            
            else: # Result should be unchanged since context is different                
                self.assertEqual(result.getX(), 500)
                self.assertEqual(result.getY(), 500)
                self.assertEqual(result.getW(), 100)
                self.assertEqual(result.getH(), 100)

    def testSpacialAboveWithProximiterAndLimitAppliedToContextOnly(self):        
        """ Test spacial attributes are applied to context only """

        region = Region(500,500,100,100)
        transform = Transform({ \
                Transform.CONTEXT_PREVIOUS: [], \
                Transform.CONTEXT_CURRENT: [], \
                Transform.CONTEXT_NEXT: [ \
                    RegionAbove(50), \
                                          ] \
              })   

        for context in self.contexts:

            result = transform.apply(region, context)
                         
            if context == Transform.CONTEXT_NEXT: # Result should change since this is the context
                self.assertEqual(result.getX(), 500)
                self.assertEqual(result.getY(), 450)
                self.assertEqual(result.getW(), 100)
                self.assertEqual(result.getH(), 50) 
            
            else: # Result should be unchanged since context is different                
                self.assertEqual(result.getX(), 500)
                self.assertEqual(result.getY(), 500)
                self.assertEqual(result.getW(), 100)
                self.assertEqual(result.getH(), 100)

    def testSimilarityAppliedToSearchContextOnly(self):
        
        pattern = Pattern("baseline/Test/Similarity.png")
        transform = Transform({ \
                Transform.CONTEXT_PREVIOUS: [], \
                Transform.CONTEXT_CURRENT: [ \
                    PatternSimilarity(1.0)
                                             ], \
                Transform.CONTEXT_NEXT: [ \
                                          ] \
              })   

        for context in self.contexts:

            if context == Transform.CONTEXT_CURRENT: # Result should change since this is the context
                result = transform.apply(pattern, context)
                self.assertEqual(str(result), 'Pattern("baseline/Test/Similarity.png").similar(1.0)')            
            else: # Rest are spacial contexts search, search_next, search_prev
                # Should raise an exception beacuse we're trying do a similarity transform on a spacial context                
                self.assertRaises(Exception, Transform.apply, (pattern, context))
        
    def testRegionMorph(self):
        
                
        region = Region(100,100,100,100)        
        region = RegionMorph(5,5,0,0).apply(region)
        
        self.assertEqual(region.getX(), 105)
        self.assertEqual(region.getY(), 105)
        self.assertEqual(region.getW(), 95)
        self.assertEqual(region.getH(), 95)        
        
        region = RegionMorph(0,0,5,5).apply(region)
        
        self.assertEqual(region.getX(), 105)
        self.assertEqual(region.getY(), 105)
        self.assertEqual(region.getW(), 100)
        self.assertEqual(region.getH(), 100)       
        
        region = RegionMorph(0,0,5,5).apply(region)
         
    def testRegionLimitByParentSmallerXY(self):        
        
        startingRegion = Region(0,0,200,200)        

        region = RegionLimitByParent().apply(startingRegion, entity=Test(Region(1,1,1,1), Test(Region(5,5,5,5), Test(Region(125,125,75,75)))))      
        self.assertEqual(region.getX(), 5)
        self.assertEqual(region.getY(), 5)
        self.assertEqual(region.getW(), 5)
        self.assertEqual(region.getH(), 5)

        
        region = RegionLimitByParent(5).apply(startingRegion, entity=Test(Region(1,1,1,1), Test(Region(5,5,5,5), Test(Region(125,125,75,75)))))        
        self.assertEqual(region.getX(), 125)
        self.assertEqual(region.getY(), 125)
        self.assertEqual(region.getW(), 75)
        self.assertEqual(region.getH(), 75)        
        
       
    def testRegionLimitByParentSmallerWidth(self):
        
        
        startingRegion = Region(0,0,50,50)        
        
        region = RegionLimitByParent().apply(startingRegion, entity=Test(Region(1,1,1,1), Test(Region(5,5,5,5), Test(Region(0,0,75,75)))))      
        self.assertEqual(region.getX(), 5)
        self.assertEqual(region.getY(), 5)
        self.assertEqual(region.getW(), 5)
        self.assertEqual(region.getH(), 5)
        
        region = RegionLimitByParent(5).apply(startingRegion, entity=Test(Region(1,1,1,1), Test(Region(5,5,5,5), Test(Region(0,0,75,75)))))        
        self.assertEqual(region.getX(), 0)
        self.assertEqual(region.getY(), 0)
        self.assertEqual(region.getW(), 50)
        self.assertEqual(region.getH(), 50)        
        
    def testRegionPreviouslyMatchedExpansion(self):
        
        previousMatches = [Region(0,0,1,1), Region(0,50,1,1)]
        
        region = Region(75,0,1,1)        
        region = RegionPreviouslyMatched().apply(region, previousMatches=previousMatches)
        
        self.assertEqual(region.getX(), 0)
        self.assertEqual(region.getY(), 0)
        self.assertEqual(region.getW(), 76)
        self.assertEqual(region.getH(), 51)
        
    def testRegionPreviouslyMatchedDoesNotAffectLarger(self):
        
        previousMatches = [Region(25,25,1,1), Region(35,35,1,1)]
        
        region = Region(0,0,50,50)        
        region = RegionPreviouslyMatched().apply(region, previousMatches=previousMatches)
        
        self.assertEqual(region.getX(), 0)
        self.assertEqual(region.getY(), 0)
        self.assertEqual(region.getW(), 50)
        self.assertEqual(region.getH(), 50)
        
    def testRegionParent(self):         
        
        testEntity = Test(Region(1,1,1,1), Test(Region(2,2,2,2), Test(Region(3,3,3,3))))
        
        region = RegionParent().apply(None, entity=testEntity)
                
        self.assertEqual(region.getX(), 2)
        self.assertEqual(region.getY(), 2)
        self.assertEqual(region.getW(), 2)
        self.assertEqual(region.getH(), 2)  
        
        region = RegionParent(2).apply(None, entity=testEntity)
                
        self.assertEqual(region.getX(), 3)
        self.assertEqual(region.getY(), 3)
        self.assertEqual(region.getW(), 3)
        self.assertEqual(region.getH(), 3)
        
        region = RegionParent(23).apply(None, entity=testEntity)
                
        self.assertEqual(region.getX(), 3)
        self.assertEqual(region.getY(), 3)
        self.assertEqual(region.getW(), 3)
        self.assertEqual(region.getH(), 3)
    
    def testRegionScreen(self):
        
        class Config(object):
            def setScreen(self, screen):
                self.screen = screen            
            def getScreen(self):
                return self.screen
        
        # Setup Config mock    
        config = Config()
        config.setScreen(Region(2,3,4,5))
        
        # Inject config dependancy
        RegionScreen.setConfig(config)
        
        # Apply transform
        region = RegionScreen().apply(Region(1,1,1,1))
        
        self.assertEqual(region, config.getScreen())
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()