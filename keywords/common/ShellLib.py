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
import sikulifw.bootstrap # Startup sikulifw
import time
from core.lib.robotremoteserver import RobotRemoteServer
import os
import string
import subprocess
import sys
from sikulifw.log import Logger

class Command(object):
    
    workingDir = ""
    parameters = None
    shellMode = True

    def __init__(self):
        self.parameters = []
    
    def setWorkingDirectory(self, path):
        self.workingDir = path
        
    def getWorkingDirectory(self):
        return os.getcwd() + '/' + self.workingDir
    
    def setShellMode(self, mode):
        self.shellMode = mode
        
    def getShellMode(self):
        return self.shellMode

    def addParameter(self, parameter):
        inQuote = False
        buildParam = ""
        for char in parameter:            
            
            if char == ' ' and len(buildParam) and not inQuote:
                self.parameters.append(buildParam)
                buildParam = ""
            elif char == '"' and not inQuote:
                inQuote = True
                buildParam = buildParam + char
            elif char == '"' and inQuote:
                # End of a quote, add the param
                inQuote = False
                buildParam = buildParam + char
                self.parameters.append(buildParam)
                buildParam = ""
            elif char == ' ' and not len(buildParam):
                pass # Don't add whitespace to start of a param
            else:            
                buildParam = buildParam + char
        
        # If there is left in the build param, add it as a param
        if len(buildParam):
            self.parameters.append(buildParam)
        
    def getParameters(self):
                
        if self.shellMode:
            # In shell mode it wants it as a string
            return ' '.join(self.parameters)
        else:
            # Otherwise as an array
            return self.parameters
            
    def __str__(self):
        
        return ' '.join(self.parameters)

       

class ShellLib(object):
    
    log = None
    command = None
    
    def __init__(self):        
        self.logger = Logger()
        
    def newCommand(self):        
        self.command = Command()
        
    def setWorkingDirectory(self, path):
        self.command.setWorkingDirectory(path)
        
    def addParameter(self, value):        
        self.command.addParameter(value)
        self.logger.info(str(self.command))
        
    def enableShellMode(self):
        self.command.setShellMode(True)

    def disableShellMode(self):
        self.command.setShellMode(False)
           
    def execute(self):
        
        self.logger.info("Executing.. [%s] wd=%s" % (self.command, self.command.getWorkingDirectory()))
        
        p = subprocess.Popen(self.command.getParameters(), shell=self.command.getShellMode(), cwd=self.command.getWorkingDirectory(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        
        if out: self.logger.info(out)
        if err: self.logger.error(err)
                
        if p.returncode != 0:
            raise Exception("Error occurred while trying to execute console command RC=%d" % p.returncode)
 
        
if __name__ == "__main__":
    RobotRemoteServer(ShellLib(), *sys.argv[1:])
