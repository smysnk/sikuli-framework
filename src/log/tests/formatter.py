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

from sikuli.Region import Region
from org.sikuli.script import Pattern
from sikuli.Screen import Screen
from entity.entities import Button, Application, Window
from entity import Entity
from log import Logger
from config import Config
from region.tests.mockFinder import Finder
from tests.mockTool import Tool
from log.level import INFO
from log.formatter import Formatter

class OuterSkin(Window):
    pass

class Apple(Window):
    
    statusCascade = True
    
    SEEDS = ['seeds', Button]
    JUICE = ['juice', Button]
    STEM = ['stem', Button]
    OUTER_SKIN = [OuterSkin]    
    AMBIGUOUS = ['ambiguous', Button]
    

class Orange(Window):
    
    SLICE = ['slice', Button]    
    AMBIGUOUS = ['ambiguous', Button]

class FruitBowl(Application):
    
    shared_state = {}
    
    APPLE = [Apple]
    ORANGE = [Orange]
   

class FormatterTests(unittest.TestCase):
    
    entity = None

    def setUp(self):

        # Setup mock objects
        
        Tool.setAssetName("md5.png")
        Formatter.setTool(Tool)
        Formatter.setConfig(Config)
        Formatter.setDefaultLevel(INFO)        

        Entity.setRegionFinderStrategy(Finder)
        Entity.setLogger(Logger)
        
        Finder.setTest(self)
        

    def tearDown(self):        
        pass
    
    def testDefaultTitle(self):
        
        # Decorator should show the default title 'FruitBowl'
        entity = FruitBowl(None)
        self.assertEqual(str(Formatter(entity)), '[FruitBowl:Application](md5.png:Actual)')
        
    def testCanSetTitleOfEntity(self):
        
        entity = FruitBowl(None)   
        
        # Test Default title 'FruitBowl:Application'
        formatter = Formatter(entity)        
        self.assertEqual(str(formatter), '[FruitBowl:Application](md5.png:Actual)')
        
        # Decorator should modify the title to 'CustomTitle'
        formatter.setLabel("CustomTitle")             
        self.assertEqual(str(formatter), '["CustomTitle"](md5.png:Actual)')
        
    def testCanDisplayBaseline(self):
                
        entity = FruitBowl(None)     
        
        rf = entity.getRegionFinder()
        rf.addBaseline("fruitbowl[0]-0", 0)
        rf.addBaseline("fruitbowl[0]-1", 0)
        rf.addBaseline("fruitbowl[1]-0", 1)
        rf.addBaseline("fruitbowl[1]-1", 1)
        rf.addBaseline("fruitbowl[1]-2", 1)
        
        # Should show the baselines for series 0
        formatter = Formatter(entity).showBaseline(True, series=0, state=None)        
        self.assertEqual(str(formatter), '[FruitBowl:Application](md5.png:series_0,md5.png:series_0)') 

        # Should display the baseline images for series 1
        formatter.showBaseline(True, series=1, state=None)
        self.assertEqual(str(formatter), '[FruitBowl:Application](md5.png:series_1,md5.png:series_1,md5.png:series_1)')        

        # Should no longer show the baselines
        formatter.showBaseline(False)
        self.assertEqual(str(formatter), '[FruitBowl:Application]()')
        
        entity.validate()
        
        # Should display the baseline images for series 0
        formatter = Formatter(entity).showBaseline(True, series=0, state=None)
        self.assertEqual(str(formatter), '[FruitBowl:Application](md5.png:Actual,md5.png:series_0,md5.png:series_0)')        

        # Should display the baseline images for series 1
        formatter.showBaseline(True, series=1, state=None)
        self.assertEqual(str(formatter), '[FruitBowl:Application](md5.png:Actual,md5.png:series_1,md5.png:series_1,md5.png:series_1)')        

        # Should no longer show the baselines
        formatter.showBaseline(False)
        self.assertEqual(str(formatter), '[FruitBowl:Application](md5.png:Actual)')
        
        
    def testFormatterCanDisplayStringEntity(self):
        
        # Should display the string that we supplied as the constructor
        formatter = Formatter("Test")
        self.assertEqual(str(formatter), '["Test"]()')
        
        # NewLabel should override the entity string name
        formatter.setLabel("NewLabel")
        self.assertEqual(str(formatter), '["NewLabel"]()')

    def testCanDisplayNone(self):
        
        # Should be able to display None
        formatter = Formatter(None)
        self.assertEqual(str(formatter), '[None]()' )    
                            
    def testCanDisplayRegionFinder(self):
        
        entity = FruitBowl(None)
        rf = entity.getRegionFinder()
        rf.addBaseline("fruitbowl[0]-0", 0)
        rf.addBaseline("fruitbowl[0]-1", 0)
        rf.addBaseline("fruitbowl[1]-0", 1)
        rf.addBaseline("fruitbowl[1]-1", 1)
        rf.addBaseline("fruitbowl[1]-2", 1)
        
        # NewLabel should override the entity string name
        formatter = Formatter(entity)
        self.assertEqual(str(formatter), '[FruitBowl:Application](md5.png:Actual)')
        
        # NewLabel should override the entity string name
        formatter.setLabel("MyImageRegion")
        self.assertEqual(str(formatter), '["MyImageRegion"](md5.png:Actual)')
    
    def testCanDisplayScreen(self):
        
        # Should have simplified Screen coords and a md5 of active region
        screen = Screen(0)
        formatter = Formatter(screen)
        self.assertEqual(str(formatter), '["Screen(0)[0,0 1680x1050]"](md5.png:Actual)')
        

    def testCanDisplayRegion(self):
        
        # Should have simplified Region coords and a md5 of active region
        formatter = Formatter(Region(0,0,100,100))
        self.assertEqual(str(formatter), '["Region[0,0 100x100]"](md5.png:Actual)')
        
    def testCanDisplayPattern(self):
        
        # Should have and a md5 of the path the pattern refers to
        formatter = Formatter(Pattern("C:/image.png"))
        self.assertEqual(str(formatter), '["Pattern("C:/image.png").similar(0.7)"](md5.png)')
        
        

        
    
        
        