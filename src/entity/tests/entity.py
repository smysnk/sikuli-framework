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
from entity import Entity, Application, Button
from region.tests.mockFinder import Finder
import tests

class EntityTests(unittest.TestCase):
    
    entity = None

    def setUp(self):        
        Finder.setTest(self)        

    def tearDown(self):        
        pass
        
    def testEntityCanInitalizeNamed(self):

        class Marble(Entity):
            pass
                
        class Jar(Application):
            shared_state = {}            
            MARBLE = [Marble]
        
        jar = Jar()
        self.assertEqual(type( jar[Jar.MARBLE] ), type(Marble(None)), "The resulting entity should be of type Jar()")

    def testEntityCanInitializeGeneric(self):
        
        class Jar(Application):
            shared_state = {}            
            MARBLE = ['marble', Button]        
        
        jar = Jar()
        marble = jar[Jar.MARBLE]
        self.assertEqual(type( marble ), type(Button(None)), "The marble should be of button type")
        self.assertEqual(marble.getName(), 'marble', "The marble should have the name 'marble'")


    def testEntityStatusDoesNotCascade(self):
        
        class Marble(Entity):
            pass
                
        class Jar(Application):
            shared_state = {}            
            MARBLE = [Marble]           
        
        jar = Jar()
        
        # Test marble doesn't status cascade
        marble = jar[Jar.MARBLE]
        marble.validate()        
        self.assertEqual(marble.isValid(), True, "The marble should be valid after we have validated")
        self.assertEqual(jar.isValid(), False, "Since we have don't have a status cascade on marble, the jar should not be validated")
        
    def testEntityStatusCascade(self):
        
        class Marble(Entity):
            statusCascade = True
                
        class Jar(Application):
            shared_state = {}            
            MARBLE = [Marble]         
       
        """
        
        More complex way of testing this, to check the order of validation (maybe not nessessary?)
        
        # Add order that we expect to find that the ImageRegion class will be invoked and by who 
        callback = lambda test, invoker=None, **kwargs: test.assertEqual(type(invoker), type(Jar()), "FruitBowl invokes ImageRegion first due to status cascade")    
        mock.RegionFinder.addCallback(callback)            
        callback = lambda test, invoker=None, **kwargs: test.assertEqual(type(invoker), type(Marble(None)), "Apple invokes ImageRegion second due to status cascade")    
        mock.RegionFinder.addCallback(callback)
        """
            
        # Test that apple status cascades and the order in which entities are validated (Jar first then Marble due to status cascade)
        jar = Jar()
        marble = jar[Jar.MARBLE]
        marble.validate()              
                
        self.assertEqual(jar.isValid(), True, "The jar should be valid after we have validated")
        self.assertEqual(marble.isValid(), True, "Since we have a status cascade on marble, the fruit bowl should be validated too")
        
    
    def testEntityFindByNameUsingSingleWordIsNotAmbiguous(self):        
        """
        Search using a key that will match more than one entity. eg (SPECK & RED_SPECK) in Marble.
        We should expect that SEEDS should be returned because less search words is more sepecific.
        """
        
        class Marble(Entity):
            RED_SPECK = ['redSpeck', Button]
            SPECKLE = ['speckle', Button]
            SPECK = ['speck', Button]
        
        print type(Marble(None))
        
        entity = Marble(None)
        
        speck = entity["speck"]
        self.assertEqual(speck.getName(), 'speck', "The single button instance named 'speck' should be returned")
       
    def testEntityFindByNameUsingMoreSpecificTerms(self):        
        """
        To remove ambiguity with which seeds to return, we add in the word 'juice' and it should rule out the SEEDS entity
        """
        
        class Marble(Entity):
            RED_SPECK = ['redSpeck', Button]
            SPECKLE = ['speckle', Button]
            SPECK = ['speck', Button]
        
        entity = Marble(None)
        
        subEntity = entity["red speck"]
        self.assertEqual(subEntity.getName(), 'redSpeck', "Our more specific search terms should return 'red speck' button")       
        

    def testEntityGetResult(self):
                
        class Shard(Entity):
            pass
        
        class Marble(Entity):
            CRACK = ['crack', Button, {'result':Shard}]
        
        marble = Marble(None)
        shard = marble[Marble.CRACK].getResult()
        
        self.assertEqual(shard.getName(), 'Shard')
        
    def testEntityGetMultiResultWithCustomParent(self):
                
        class Shard(Entity):
            pass
        
        class RedMarble(Entity):
            pass
        
        class PinkMarble(Entity):
            pass        
        
        class GreenMarble(Entity):
            CRACK = ['crack', Button, {'result':[(Shard,RedMarble(None)), PinkMarble]}]
        
        marble = GreenMarble(None)
        proxy = marble[GreenMarble.CRACK].getResult()
        shard = proxy[Shard]
        
        self.assertEqual(shard.getName(), 'Shard')
        self.assertEqual(shard.getParent().getName(), 'RedMarble')
        
    def testEntityGetLambdaResult(self):
                
        class Shard(Entity):
            pass
        
        class Marble(Entity):
            CRACK = ['crack', Button, {'result':lambda: Shard}]
        
        marble = Marble(None)
        shard = marble[Marble.CRACK].getResult()
        
        self.assertEqual(shard.getName(), 'Shard')
        
        
    def testEntityGetLambdaInstantiatedResult(self):
                
        class Shard(Entity):
            pass
        
        class Marble(Entity):
            CRACK = ['crack', Button, {'result':lambda: Shard(None)}]
        
        marble = Marble(None)
        shard = marble[Marble.CRACK].getResult()
        
        self.assertEqual(shard.getName(), 'Shard')        
        
    def testEntityGetMultiResultWithLambdaResultAndCustomParentLamda(self):
                
        class Shard(Entity):
            pass
        
        class RedMarble(Entity):
            pass
        
        class Marble(Entity):
            CRACK = ['crack', Button, {'result': (lambda:Shard, lambda parent: parent.getParent()) }]
        
        
        marble = Marble(RedMarble(None))
        shard = marble[Marble.CRACK].getResult()
        
        self.assertEqual(shard.getName(), 'Shard')    
        self.assertEqual(shard.getParent().getName(), 'RedMarble')
         
    def testEntityGetMultiResultWithLambdaResultAndCustomParent(self):
                
        class Shard(Entity):
            pass
        
        class RedMarble(Entity):
            pass
        
        class PinkMarble(Entity):
            pass
        
        class GreenMarble(Entity):
            CRACK = ['crack', Button, {'result':[ (lambda: Shard, RedMarble(None)), PinkMarble ]}]
        
        marble = GreenMarble(None)
        proxy = marble[GreenMarble.CRACK].getResult()
        shard = proxy[Shard]
        
        self.assertEqual(shard.getName(), 'Shard')
        self.assertEqual(shard.getParent().getName(), 'RedMarble')

    def testEntityGetMultiResultWithCustomParentLamda(self):
                
        class Shard(Entity):
            pass
        
        class RedMarble(Entity):
            pass
        
        class GreenMarble(Entity):
            CRACK = ['crack', Button, {'result':[ (Shard,lambda parent: parent.getParent()) ]}]
        
        marble = GreenMarble(RedMarble(None))
        proxy = marble[GreenMarble.CRACK].getResult()
        shard = proxy[Shard]
        
        self.assertEqual(shard.getName(), 'Shard')
        self.assertEqual(shard.getParent().getName(), 'RedMarble')

