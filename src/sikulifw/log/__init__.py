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

from level import *
import robotFramework
import string

class Logger(object):
    
    entity = None
    logger = None
    formatter = None
    
    @classmethod
    def setRobotLogger(cls, robotLogger):
        cls.robotLogger = robotLogger
        
    @classmethod
    def getRobotLogger(cls):
        return cls.robotLogger
    
    @classmethod    
    def setFormatter(cls, formatter):
        cls.formatter = formatter
    
    @classmethod
    def getLevel(cls):
        return cls.robotLogger.getEffectiveLevel()
        
    @classmethod
    def setLevel(self, level):
        self.robotLogger.setLevel(level)
        self.robotLogger.log(level, None, "Changing logging level")     
    
    def __init__(self, entity=None, level=None):
        """ Originally we had a singleton logger model, but to support binding entities to a logger
        it is best to create a entirely new instance of the logger """
        
        self.entity = entity    # associate an entity with this logger
        
        if level:
            self.setLevel(level)
            
    def setEntity(self, entity):
        self.entity = entity   
            
    def log(self, level, msg, *args, **kwargs):
        
        # Set formatter to the logging level of this log statement    
        for arg in args:
            arg.setLogLevel(level)        
        
        # Remove extra % 
        if len(args) > 0: # if there are no args supplied for str replacement, don't even try
            msg = string.replace(msg, r'%%s',r'%s')
            msg = msg % args
        
        # Formulate the prefix for this log statement
        prefix = "%s " % str(self.formatter(self.entity).setLogLevel(level)) if self.entity else ''        
        
        self.robotLogger.log(level, prefix + msg, *args, **kwargs)
        
    def info(self, msg, *args, **kwargs):
        """ Override to support keywords """  
        self.log(INFO, msg, *args, **kwargs)
            
    def warn(self, msg, *args, **kwargs):
        """ Override to support keywords """
        self.log(WARN, msg, *args, **kwargs) 
    
    def debug(self, msg, *args, **kwargs):
        """ Override to support keywords """        
        self.log(DEBUG, msg, *args, **kwargs)
    
    def trace(self, msg, *args, **kwargs):
        self.log(TRACE, msg, *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        """ Override to support keywords """
        self.log(ERROR, msg, *args, **kwargs)        
        
    def getFormatter(self):
        return self.formatter

        