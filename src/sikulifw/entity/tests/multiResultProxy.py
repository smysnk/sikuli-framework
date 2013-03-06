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
from sikulifw.entity import Entity
from sikulifw.entity import Button
from sikulifw.entity.multiResultProxy import MultiResultProxy

import sikulifw.tests


class MultiResultProxyTest(unittest.TestCase):


    def setUp(self):
        pass

    def tearDown(self):
        pass
    
    
    def testResultParent(self):

        class GreenMarble(Entity):
            GREEN_SPECK = ['greenSpeck', Button]

        class RedMarble(Entity):
            RED_SPECK = ['redSpeck', Button]
            
        class BlueMarble(Entity):
            BLUE_SPECK = ['blueSpeck', Button]            

        proxy = MultiResultProxy(None, [(RedMarble, BlueMarble(None)),(GreenMarble, BlueMarble(None))], None)
        
        result = proxy[RedMarble.RED_SPECK]        
        self.assertEqual(result.getName(), 'redSpeck')
        self.assertEqual(result.getParent().getParent().getName(), 'BlueMarble')
    
        result = proxy[GreenMarble.GREEN_SPECK]        
        self.assertEqual(result.getName(), 'greenSpeck')
        self.assertEqual(result.getParent().getParent().getName(), 'BlueMarble')
    
        #proxy.find
        
            

    def testFindClassFromKey(self):

        class RedMarble(Entity):
            RED_SPECK = ['redSpeck', Button]
            
        class BlueMarble(Entity):
            BLUE_SPECK = ['blueSpeck', Button]            

        proxy = MultiResultProxy(None, [RedMarble, BlueMarble], None)
        
        # Supplying the RED_SPECK keyword will return the RedMarble class that it belongs to
        result = proxy[RedMarble.RED_SPECK]
        self.assertEqual(result.getName(), 'redSpeck')
        
        # Suppling the BLUE_SPEC keyword will return the BlueMarble class that it belongs to
        result = proxy[BlueMarble.BLUE_SPECK]
        self.assertEqual(result.getName(), 'blueSpeck')
    
    def testFindClassFromAmbiguousKeyReturnsError(self):

        class RedMarble(Entity):
            SPECK = ['speck', Button]
            
        class BlueMarble(Entity):
            SPECK = ['speck', Button]            

        
        proxy = MultiResultProxy(None, [RedMarble, BlueMarble], None)
                
        # Make sure finding a class from ambiguous key raises exception
        self.assertRaises(Exception, proxy.__getitem__, RedMarble.SPECK)
        self.assertRaises(Exception, proxy.__getitem__, BlueMarble.SPECK)
        
    def testPassingNullKeyRaisesException(self):
        
        class RedMarble(Entity):
            SPECK = ['speck', Button]
            
        class BlueMarble(Entity):
            SPECK = ['speck', Button]         
        
        proxy = MultiResultProxy(None, [RedMarble, BlueMarble], None)
        
        # Passing an None key will return raise an EntityNotFound exception
        self.assertRaises(Exception, proxy.__getitem__, None)        
                  
                  
    def testPassingProxyInvalidKeyRaisesException(self):
        
        class RedMarble(Entity):
            SPECK = ['speck', Button]
            
        class BlueMarble(Entity):
            SPECK = ['speck', Button]         
        
        proxy = MultiResultProxy(None, [RedMarble, BlueMarble], None)
          
        # Passing an invalid key will return raise an EntityNotFound exception
        self.assertRaises(Exception, proxy.__getitem__, ['failEntity',Button])
      

if __name__ == "__main__":
    unittest.main()
    