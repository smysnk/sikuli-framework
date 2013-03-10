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
from keywords.common.ShellLib import *

class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testCanAddBasicParameters(self):
        
        command = Command()
        command.setShellMode(False)
        command.addParameter("param1")
        command.addParameter("param2")
        command.addParameter("param3")
        
        self.assertEqual(command.getParameters(), ['param1','param2','param3'])
        
        
    def testCanAddCompoundParameters(self):
        
        command = Command()
        command.setShellMode(False)
        command.addParameter("param1 param2")
        command.addParameter("param3")
        command.addParameter("param4")
        
        self.assertEqual(command.getParameters(), ['param1','param2','param3','param4'])

    def testCanAddQuoteParameter(self):
        
        command = Command()
        command.setShellMode(False)
        command.addParameter('"quote param"')
        
        self.assertEqual(command.getParameters(), ['quote param'])

    def testCanAddCompoundQuoteParameter(self):
        
        command = Command()
        command.setShellMode(False)
        command.addParameter('param1 "quote param2" param3')
        
        self.assertEqual(command.getParameters(), ['param1','quote param2','param3'])

    def testShell(self):
        
        command = Command()
        command.addParameter('msiexec.exe')
        command.addParameter(unicode('/i "test.msi"'))
        
        print str(command)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
    
