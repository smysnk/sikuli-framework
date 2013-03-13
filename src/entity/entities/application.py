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
from entity import Entity
from wrapper import Env
import re
from org.sikuli.script import OS

class Application(Entity):
    """ Application Entitiy """
    
    # For borg/singleton pattern
    shared_state = None

    family = True
    pid = None
    applicationProcess = None
    processMonitor = None

    binary = {
              OS.WINDOWS : None, #'SMART Technologies/Education Software/Notebook.exe'
              OS.MAC : None, #'SMART Technologies/Notebook.app'
              OS.LINUX : None #'/opt/SMART Technologies/SMART Notebook/bin/notebook'
            }
    
    workingDir = {
                  OS.WINDOWS : None,
                  OS.MAC : None,
                  OS.LINUX: None,
                }
        
    def __init__(self, *args, **kargs):
        self.__dict__ = self.shared_state # borg pattern, singleton   
        if self.region: return # singleton hackin
                            
        super(Application, self).__init__(None, *args, **kargs)        
    
    def setApplicationProcess(self, process, monitor=True):
        self.applicationProcess = process
        
        match = re.search(r"\(([0-9]*)\)", str(process))
        if match and match.group(1):
            self.pid = int(match.group(1))
        else:
            raise Exception("Unable to match process id")
        
        # Add to performance monitor
        if monitor:            
            self.processMonitor.add(self.pid)
        
        
    def getApplicationProcess(self):
        return self.applicationProcess
    
    def getPid(self):
        return self.pid

    def getBinary(self, os, osVersion, arch):
        return self.parsePath(os, osVersion, arch, self.binary[os])
        
    def getWorkingDir(self, os, osVersion, arch):
        if self.workingDir[os]:
            return self.parsePath(os, osVersion, arch, self.workingDir[os])
        else:
            return None

    def parsePath(self, os, osVersion, arch, path):        
        if path[:1] == '/' or path[:3].lower() == 'c:\\':
            pass # absolute path        
        elif os == OS.WINDOWS and (arch == 'x64' or osVersion == "XP"):
            path = path.replace('<%Program Files%>', 'c:/Program Files')    
        elif os == OS.WINDOWS and arch == 'x86':
            path = path.replace('<%Program Files%>', 'c:/Program Files (x86)')
        elif os == OS.MAC:
            path = path.replace('<%Program Files%>', '/Applications')
        
        return path