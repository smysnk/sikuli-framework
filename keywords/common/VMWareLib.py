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
from core.lib.robotremoteserver import RobotRemoteServer
import sikulifw.bootstrap # Startup sikulifw
from sikulifw.entity import *

import os
import sys
import subprocess
import platform
from sikulifw.log import Logger
from maps.common.vmware import VMWare
from keywords.sikulifwLib import sikulifwLib


class VMWareLib(sikulifwLib):
    
    vmrunPath = None
    log = Logger()
    namespace = ""
    entity = None

    def __init__(self):
        super(VMWareLib, self).__init__()
        """Also this doc should be in shown in library doc."""
        self.entity = VMWare()
        
    def setNamespace(self, namespace):
        self.namespace = namespace
    
    def stopAll(self):
        """
        Stop all virtual machines
        """
   
        self.log.info("Getting a list of all running snapshots.")
        p = subprocess.Popen(['vmrun', 'list'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        
        # Display output from vmrun
        self.log.info(out)
        
        if not err:            
            # Iterrate over all running virtual machines
            for match in re.finditer(r"(?im)(^.*?\.vmx$)", out):
                # match start: match.start()
                # match end (exclusive): match.end()
                # matched text: match.group()
                
                self.log.info("Stopping virtual machine. vm=%s" %  match.group())
                p = subprocess.Popen(['vmrun', 'suspend', match.group()], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = p.communicate()

                if out: self.log.info(out)
                if err: self.log.error(err)                                       
        else:
            self.log.error("err:" + err)
                
    
    def getSnapshotName(self, snapshotName):
        
        reobj = re.compile("'(?P<snapshot>.*)'", re.IGNORECASE)
        result = reobj.search(snapshotName)
        
        if result and result.group("snapshot"):
            return result.group("snapshot")
        elif self.namespace:
            return "%s-%s" % (self.namespace, snapshotName)
        else:
            return snapshotName
       
    def revertSnapshot(self, imagePath, snapshotName):
        
        self.log.info("Attempting to revert snapshot. vm=%s snapshot=%s" % (imagePath, self.getSnapshotName(snapshotName)))
        p = subprocess.Popen(['vmrun', 'revertToSnapshot', imagePath, self.getSnapshotName(snapshotName)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        
        if out: self.log.info(out)
        if err: self.log.error(err)
                
        if p.returncode != 0:        
            raise Exception("Error reverting snapshot, RC=%d" % p.returncode)
                
        p = subprocess.Popen(['vmrun', 'start', imagePath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        
        if out: self.log.info(out)
        if err: self.log.error(err)
                
        if p.returncode != 0:
            raise Exception("Error starting VM, RC=%d" % p.returncode)

    def createSnapshot(self, imagePath, snapshotName):
        
        p = subprocess.Popen(['vmrun','snapshot', imagePath, self.getSnapshotName(snapshotName)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        
        if out: self.log.info(out)
        if err: self.log.error(err)
                
        if p.returncode != 0:
            raise Exception("Error creating snapshot, RC=%d" % p.returncode)
        
        
    def deleteSnapshot(self, imagePath, snapshotName, deleteChildren=True):
        
        # VM must be suspended before we can delete it
        p = subprocess.Popen(['vmrun','suspend', imagePath, 'hard'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        
        if out: self.log.info(out)
        if err: self.log.error(err)
                
        if p.returncode != 0:
            #raise Exception("Error suspending snapshot, RC=%d" % p.returncode)
            self.log.warn("Error suspending [%s] snapshot, RC=%d" % (self.getSnapshotName(snapshotName), p.returncode))
        
        
        # Delete the snapshot
        args = ['vmrun','deleteSnapshot', imagePath, self.getSnapshotName(snapshotName)]
        
        if deleteChildren:  args.append('andDeleteChildren')
        
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        
        if out: self.log.info(out)
        if err: self.log.error(err)
                
        if p.returncode != 0:
            self.log.warn("Error deleting [%s] snapshot, RC=%d" % (self.getSnapshotName(snapshotName), p.returncode))
        
    
        
if __name__ == '__main__':
    RobotRemoteServer(VMWareLib(), *sys.argv[1:])

    #remoteLib = ExampleRemoteLibrary()
    #remoteLib.revertSnapshot()
    #remoteLib.start()
