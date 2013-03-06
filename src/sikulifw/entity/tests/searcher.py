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
from sikuli.Region import Region
from sikulifw.entity.searcher import Searcher, AmbiguousKeySearchException, KeyNotFoundException
from sikulifw.entity import Entity, Button
from sikulifw.entity.multiResultProxy import MultiResultProxy
import sikulifw.tests
import inspect

class SearcherTest(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass

    def testSearchWithClass(self):
        
        class BlueMarble(Entity):
            BLUE_SPECK = ['blueSpeck', Button]

        es = Searcher()
        es.add(BlueMarble)
        result = es.search(BlueMarble)
        
        # Should return the entity with the least number of words
        self.assertEqual(result.getEntity(), [BlueMarble,])


    def testSearchWithMemberVariable(self):
        
        class BlueMarble(Entity):
            BLUE_SPECK = ['blueSpeck', Button]

        class RedMarble(Entity):
            RED_SPECK = ['redSpeck', Button]

        es = Searcher()
        es.add(BlueMarble)
        es.add(RedMarble)
        result = es.search(BlueMarble.BLUE_SPECK)
        
        # Should return the entity with the least number of words
        self.assertEqual(result.getEntity(), BlueMarble.BLUE_SPECK)


    def testSearchWithMemberVariableAmbiguousException(self):
        
        class BlueMarble(Entity):
            BLUE_SPECK = ['blueSpeck', Button]

        class RedMarble(Entity):
            BLUE_SPECK = ['blueSpeck', Button]

        es = Searcher()
        es.add(BlueMarble)
        es.add(RedMarble)
        
        # Both entities have the exact same member variables, should raise ambiguous exception
        self.assertRaises(AmbiguousKeySearchException, es.search, BlueMarble.BLUE_SPECK)         
        
        
    def testSearchWithMemberVariableNotFoundException(self):
        
        class BlueMarble(Entity):
            BLUE_SPECK = ['blueSpeck', Button]

        es = Searcher()
        es.add(BlueMarble)
        
        # Search for non existent member variable key, should not return anything
        self.assertRaises(KeyNotFoundException, es.search, ['Does Not Exist', BlueMarble])          

    def testReturnsEntityWithLeastNumberOfWords(self):
        
        class RedAndBlueMarble(Entity):
            BIG_RED_SPECK = ['bigRedSpeck', Button]
            BLUE_SPECK = ['blueSpeck', Button]

        es = Searcher()
        es.add(RedAndBlueMarble)
        result = es.search("speck")
        
        # Should return the entity with the least number of words
        self.assertEqual(result.getEntity(), RedAndBlueMarble.BLUE_SPECK)
        
    def testSingleEntityAndSubEntityDefAmbiguous(self):
        

        class BlueMarble(Entity):
            BLUE_SPECK = ['blueSpeck', Button]        

        es = Searcher()
        es.add(MultiResultProxy(None, [BlueMarble], None))
        
        self.assertRaises(AmbiguousKeySearchException, es.search, "blue")
        
    def testSingleEntityAndSubEntitySpecific(self):
        
        class BlueMarble(Entity):
            BLUE_SPECK = ['blueSpeck', Button]
        
        es = Searcher()
        es.add(MultiResultProxy(None, [BlueMarble], None))
        
        result = es.search("blue marble")
        self.assertEqual(result.getEntity(), [BlueMarble])        
        

    def testMultiSearchEntityAmbiguous(self):
        
        class BlueMarble(Entity):
            BLUE_SPECK = ['blueSpeck', Button]

        class RedMarble(Entity):
            RED_SPECK = ['redSpeck', Button]

        
        es = Searcher()
        es.add(MultiResultProxy(None, [BlueMarble, RedMarble], None))
        
        self.assertRaises(AmbiguousKeySearchException, es.search, "marble")        

    def testMultiSearchSubEntityAmbiguous(self):
        
        class BlueMarble(Entity):
            BLUE_SPECK = ['blueSpeck', Button]

        class RedMarble(Entity):
            RED_SPECK = ['redSpeck', Button]

        
        es = Searcher()
        es.add(MultiResultProxy(None, [BlueMarble, RedMarble], None))
        
        self.assertRaises(AmbiguousKeySearchException, es.search, "speck") 
        
    def testMultiSearchSubEntitySpecific(self):
        
        class BlueMarble(Entity):
            BLUE_SPECK = ['blueSpeck', Button]

        class RedMarble(Entity):
            RED_SPECK = ['redSpeck', Button]

        
        es = Searcher()
        es.add(MultiResultProxy(None, [BlueMarble, RedMarble], None))
        
        result = es.search("red speck")
        self.assertEqual(result.getEntity(), RedMarble.RED_SPECK)   

        result = es.search("blue speck")
        self.assertEqual(result.getEntity(), BlueMarble.BLUE_SPECK)       
        
    def testCanSearchMultiProxyResultWithCustomParent(self):
        
        class BlueMarble(Entity):
            BLUE_SPECK = ['blueSpeck', Button]

        class RedMarble(Entity):
            RED_SPECK = ['redSpeck', Button]

        customParent = RedMarble(None)
                
        es = Searcher()
        es.add(MultiResultProxy(None, [(BlueMarble, customParent),], None))
        
        result = es.search("blue speck")
        self.assertEqual(result.getEntity(), BlueMarble.BLUE_SPECK)
        self.assertEqual(result.getParent(), customParent)               

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()