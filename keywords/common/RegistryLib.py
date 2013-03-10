#Interpreter: Python
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
from core.lib.robotremoteserver import RobotRemoteServer
import sys
import _winreg
import re

class RegistryLib(object):
    
    def setValue(self, key, type, valueName, value):
        
        # Match a registry key
        match = re.search(r"(?P<namespace>^[a-z0-9_]+)\\(?P<key>[ a-z0-9_\\]*?)$", key, re.IGNORECASE | re.MULTILINE)
        
        if not match:
            raise Exception("Key syntax is invalid")
                                
        try:
            keyRes = _winreg.CreateKey(getattr(_winreg, match.group("namespace")), match.group("key"))
            _winreg.SetValueEx(keyRes, valueName, None, getattr(_winreg,type), value)
            _winreg.CloseKey(keyRes)
            print "Key [%s\\%s], setting type [%s] value [%s=%s]" % (match.group("namespace"), match.group("key"), type, valueName, value)
        finally:
            pass

    
    def readValue(self, key, valueName):
        
        # Match a registry key
        match = re.search(r"(?P<namespace>^[a-z0-9_]+)\\(?P<key>[ a-z0-9_\\]*?)$", key, re.IGNORECASE | re.MULTILINE)
        
        if not match:
            raise Exception("Key syntax is invalid")        
        
        try:
            keyRes = _winreg.OpenKey(getattr(_winreg, match.group("namespace")), match.group("key"), 0, _winreg.KEY_ALL_ACCESS)
        except WindowsError:
            raise Exception("Cannot find registry key [%s]" % key)
        
        try:
            return _winreg.QueryValueEx(keyRes, valueName)[0]
        except WindowsError:
            raise Exception("Cannot find valueName [%s] in registry key [%s]" % (valueName, match.group("namespace")))
        
        _winreg.CloseKey(keyRes)
    
    def createKey(self, key):
        
        # Match a registry key
        match = re.search(r"(?P<namespace>^[a-z0-9_]+)\\(?P<key>[ a-z0-9_\\]*?)$", key, re.IGNORECASE | re.MULTILINE)
        
        if not match:
            raise Exception("Key syntax is invalid")        
        
        try:
            keyRes = _winreg.CreateKey(getattr(_winreg, match.group("namespace")), key)
            _winreg.CloseKey(keyRes)
            print "[%s] created." % (key)         
        finally:
            pass

if __name__ == '__main__':
    RobotRemoteServer(RegistryLib(), *sys.argv[1:])

    
