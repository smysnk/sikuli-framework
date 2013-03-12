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
import sikulifw.bootstrap # Startup sikulifw
import time
import os
import string
import subprocess
import sys
from sikulifw.log import Logger
import re

#from sikulifw.log.decorators import Formatter
from sikulifw.config import Config


class ToolsLib(object):
    
    log = None
    artifactPath = "install"
    
    def __init__(self):
        
        self.log = Logger()
        
    def findFile(self, needle, extension):

        # Find the zip file (We have to find like this because the date changes)
        found = False
        for file in os.listdir(self.artifactPath):            
            if string.find(file, needle) >= 0 and re.search(extension + "$", file, re.IGNORECASE):
                found = True
                break;
        
        if not found:
            self.log.debug("files=%s" % ','.join(os.listdir(self.artifactPath)))
            raise Exception("Unable to find a zip file that has [%s] in the name with [%s] extension" % (needle, extension))
        
        # Get the name of the file minus the extension
        reobj = re.compile(r"(?P<filename>.*?)(?P<ext>\.[0-9a-z]*$)", re.IGNORECASE)
        return reobj.search(file).group("filename")
               
   

if __name__ == "__main__":
    RobotRemoteServer(ToolsLib(), *sys.argv[1:])
    
    
    
