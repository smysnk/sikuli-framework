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
import subprocess
import os
from com.ibm.staf import STAFHandle, STAFMarshallingContext
import sys
import java
import string
import logging

class STAXLib:
        
    tempPath = "/tmp"
    tarballFilename = "test.tar"
    resultsTarballFilename = "results.tar"
    
    remotePlatformPath = "/tmp/test"
    remoteArtifactPath = "/tmp/artifacts"
    
    backupPath = string.replace(os.getcwd(), '\\', '/')
    port = '8270'
    log = logging.getLogger("stax")
    
    def setRemotePlatformPath(self, path):        
        self.remotePlatformPath = path
        self.log.info("Remote Platform Path set to [%s]" % self.remotePlatformPath)
    
    def pingHost(self, hostname):
        cwd = os.getcwd()        
        result = STAFHandle('pingHost').submit2(hostname, 'ping', 'ping')
        
        if result.rc != 0:
            raise Exception("Error pinging target [%s]. RC=%d MSG=%s" % (hostname, result.rc, str(result.result)))
        else:            
            self.log.info(result.result) # Log the result for the executed command
    
    def prepareHostUsingArtifacts(self, remoteHost):

        cwd = os.getcwd()
        artifactsPath = cwd + '/artifacts'
        artifacts = ','.join(os.listdir(artifactsPath))
        
        result = STAFHandle('prepareHost').submit2('local', 'stax', "EXECUTE FILE %s/staxScripts/prepareHostUsingArtifacts.xml FUNCTION Main ARGS \"{'remoteHost':'%s','artifacts':'%s','artifactPath':'%s','remotePlatformPath':'%s','remoteArtifactPath':'%s'}\" WAIT 20m RETURNRESULT DETAILS LOGTCELAPSEDTIME Enabled LOGTCNUMSTARTS Enabled LOGTCSTARTSTOP Enabled" % (cwd, remoteHost, artifacts, artifactsPath, self.remotePlatformPath, self.remoteArtifactPath))
                
        # Get the RC code depending on failure type
        if result.rc != 0: # STAF Failure
            self.logResultData(result.resultObj, "STAF") # Log the result for the executed command
            rc = result.rc            
        else:
            self.logResultData(result.resultObj) # Log the result for the executed command
            rc = int(result.resultObj.get('result'))            
            
        if rc != 0:
            raise Exception("Error occurred while preparing Host. RC=%d" % rc)          

    def launch(self, remoteHost, scriptPath, port=None):
        
        # Launch arguments
        args = ''
        if os.environ.get('LOGLEVEL'):
            args += '--logLevel %s ' % os.environ['LOGLEVEL']
            
        if os.environ.get('LOGLEVEL_SCREENSHOTS'):
            args += '--screenshotLogLevel %s' % os.environ['LOGLEVEL_SCREENSHOTS']
         
                    
        port = self.port if not port else port
        
        cwd = os.getcwd()        
        result = STAFHandle('prepareHost').submit2('local', 'stax', "EXECUTE FILE %s/staxScripts/launch.xml FUNCTION Main ARGS \"{'remoteHost':'%s','scriptPath':'%s','port':'%s','args':'%s','remotePlatformPath':'%s'}\" WAIT 10m RETURNRESULT DETAILS LOGTCELAPSEDTIME Enabled LOGTCNUMSTARTS Enabled LOGTCSTARTSTOP Enabled" % (cwd, remoteHost, scriptPath, port, args, self.remotePlatformPath))
                
        # Get the RC code depending on failure type
        if result.rc != 0: # STAF Failure
            rc = result.rc
            self.logResultData(result.resultObj, "STAF") # Log the result for the executed command
        else:   
            rc = int(result.resultObj.get('result'))
            self.logResultData(result.resultObj) # Log the result for the executed command
        
        if rc != 0:
            raise Exception("Error occurred while launching script. RC=%d" % rc)          
        

    def collectResults(self, remoteHost, localPlatformPath=None, testPlatformPath=None, tempPath=None, resultsTarballFilename=None):
        
        # Use member variables if the method doesn't supply them
        tempPath = self.tempPath if not tempPath else tempPath
        resultsTarballFilename = self.resultsTarballFilename if not resultsTarballFilename else resultsTarballFilename
        localPlatformPath = self.backupPath if not testPlatformPath else testPlatformPath 
        
        cwd = os.getcwd()
        result = STAFHandle('collectResults').submit2('local', 'stax', "EXECUTE FILE %s/staxScripts/collectResults.xml FUNCTION Main ARGS \"{'remoteHost':'%s','localPlatformPath':'%s','tempPath':'%s','tarballFilename':'%s','remotePlatformPath':'%s'}\" WAIT 5m RETURNRESULT DETAILS LOGTCELAPSEDTIME Enabled LOGTCNUMSTARTS Enabled LOGTCSTARTSTOP Enabled" % (cwd, remoteHost, localPlatformPath, tempPath, resultsTarballFilename, self.remotePlatformPath))
                
        # Get the RC code depending on failure type
        if result.rc != 0: # STAF Failure
            rc = result.rc
            self.logResultData(result.resultObj, "STAF") # Log the result for the executed command
        else:
            rc = int(result.resultObj.get('result'))
            self.logResultData(result.resultObj) # Log the result for the executed command
        
        if rc != 0:
            raise Exception("Error occurred while creating tarball. RC=%d" % rc)  
                    
    
    
    def logResultData(self, map, key=None):
        """ Used for displaying the result of running a STAF/STAX command """

        if isinstance(map, unicode):
            
            self.log.info("%s=%s" % (key, map))
            return
            
        elif isinstance(map, java.util.LinkedList):
            
            for item in map:                            
                self.log.info("%s=%s" % (key, item))
                
            return             
        
        for key in map:
            
            # Deal with crazy structure of results
            if isinstance(key, java.util.HashMap):
                self.logResultData(key)
                return
            else:
                #print type(map)
                value = map.get(key)
            
            if isinstance(map.get(key), unicode):
                self.log.info("%s=%s", key, value)
            elif isinstance(map.get(key), java.util.HashMap):
                self.logResultData(value)
            elif isinstance(map.get(key), java.util.LinkedList):
                self.logResultData(value, key)
            else:
                pass
                #print "%s=%s" % (key, type(value))  


if __name__ == '__main__':
    stax = STAXLib()
    stax.prepareHostNew("")
