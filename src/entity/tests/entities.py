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
from entity import Entity, Window, Button, Application
from region.tests.mockFinder import Finder
from entity.searcher import Searcher
from log import Logger

class SecondDescendant(Window):
    
    shared_state = {}
    
    CHILD = ["Child", lambda parent, **kargs: Button(parent, **kargs)]  

class SecondFamily(Window):
    
    shared_state = {}    
    family = True
    
    SECOND_DESCENDANT = [SecondDescendant, lambda parent, **kargs: SecondDescendant(parent, **kargs)]  

class FirstDescendant(Window):
    
    SECOND_FAMILY = [SecondFamily, lambda parent, **kargs: SecondFamily(parent, **kargs)]  

class FirstFamily(Window):
    
    family = True
    shared_state = {}
    
    FIRST_DESCENDANT = [FirstDescendant, lambda parent, **kargs: FirstDescendant(parent, **kargs)]

class SecondNode(Window):
    
    shared_state = {}
    
    FIRST_FAMILY = [FirstFamily, lambda parent, **kargs: FirstFamily(parent, **kargs)]

class Root(Application):

    shared_state = {}

    SECOND_NODE = [SecondNode, lambda parent, **kargs: SecondNode(parent, **kargs)]


class NameTests(unittest.TestCase):
    
    entity = None

    def setUp(self):
        Entity.setRegionFinderStrategy(Finder)
        Entity.setSearcherStrategy(Searcher)
        Entity.setLogger(Logger)
        

    def tearDown(self):        
        pass
        

    def testConanicalName(self):
        
        entity = Root()[Root.SECOND_NODE][SecondNode.FIRST_FAMILY][FirstFamily.FIRST_DESCENDANT][FirstDescendant.SECOND_FAMILY][SecondFamily.SECOND_DESCENDANT][SecondDescendant.CHILD]

        # Default args
        self.assertEqual(entity.getCanonicalName(),"Root.SecondNode.FirstFamily.FirstDescendant.SecondFamily.SecondDescendant,child")

        # Ancestor complete set (true/false)
        self.assertEqual(entity.getCanonicalName(rootEntity=True, ancestorEntities=True, topLevel=True),"Root.SecondNode.FirstFamily.FirstDescendant.SecondFamily.SecondDescendant,child")
        self.assertEqual(entity.getCanonicalName(rootEntity=True, ancestorEntities=True, topLevel=False),"Root.SecondNode.FirstFamily.FirstDescendant.SecondFamily.SecondDescendant")
        self.assertEqual(entity.getCanonicalName(rootEntity=True, ancestorEntities=False, topLevel=True),"Root,child")        
        self.assertEqual(entity.getCanonicalName(rootEntity=True, ancestorEntities=False, topLevel=False),"Root")
        self.assertEqual(entity.getCanonicalName(rootEntity=False, ancestorEntities=True, topLevel=True),".SecondNode.FirstFamily.FirstDescendant.SecondFamily.SecondDescendant,child")        
        self.assertEqual(entity.getCanonicalName(rootEntity=False, ancestorEntities=True, topLevel=False),".SecondNode.FirstFamily.FirstDescendant.SecondFamily.SecondDescendant")
        self.assertEqual(entity.getCanonicalName(rootEntity=False, ancestorEntities=False, topLevel=True),",child")        
        self.assertEqual(entity.getCanonicalName(rootEntity=False, ancestorEntities=False, topLevel=False),"")

        # Ancestor depth=2
        self.assertEqual(entity.getCanonicalName(rootEntity=True, ancestorEntities=2, topLevel=True),"Root.FirstFamily.FirstDescendant.SecondFamily.SecondDescendant,child")
        self.assertEqual(entity.getCanonicalName(rootEntity=True, ancestorEntities=2, topLevel=False),"Root.FirstFamily.FirstDescendant.SecondFamily.SecondDescendant")
        self.assertEqual(entity.getCanonicalName(rootEntity=False, ancestorEntities=2, topLevel=True),".FirstFamily.FirstDescendant.SecondFamily.SecondDescendant,child")        
        self.assertEqual(entity.getCanonicalName(rootEntity=False, ancestorEntities=2, topLevel=False),".FirstFamily.FirstDescendant.SecondFamily.SecondDescendant")

        # Ancestor depth=1
        self.assertEqual(entity.getCanonicalName(rootEntity=True, ancestorEntities=1, topLevel=True),"Root.SecondFamily.SecondDescendant,child")
        self.assertEqual(entity.getCanonicalName(rootEntity=True, ancestorEntities=1, topLevel=False),"Root.SecondFamily.SecondDescendant")
        self.assertEqual(entity.getCanonicalName(rootEntity=False, ancestorEntities=1, topLevel=True),".SecondFamily.SecondDescendant,child")        
        self.assertEqual(entity.getCanonicalName(rootEntity=False, ancestorEntities=1, topLevel=False),".SecondFamily.SecondDescendant")


    def testName(self):
        
        root = Root()
        
        self.assertEqual(root.getName(), "Root")
                
        secondNode = root[Root.SECOND_NODE]        
        self.assertEqual(secondNode.getName(), "SecondNode")
        
        firstFamily = secondNode[SecondNode.FIRST_FAMILY]
        self.assertEqual(firstFamily.getName(), "FirstFamily")
        
         
if __name__ == "__main__":
    unittest.main()
    