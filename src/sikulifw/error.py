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


import sikulifw as sikulifw

class sikulifwException(Exception):
    
    logger = None
    screenshot = None
    entity = None
    config = None
    
    @classmethod
    def setLogger(cls, logger):
        cls.logger = logger
        
    @classmethod
    def setConfig(cls, config):
        cls.config = config
    
    def __init__(self, value="", screenshot=False, entity=None, **kargs):
        
        self.value = value
        self.screenshot = screenshot
        self.entity = entity
        self.logger = self.__class__.logger(entity)

    def __str__(self):
        
        return "%s %s" % (self.logger.getFormatter()(self.config.screen), self.value)

class CreateWindowFailed(sikulifwException):
    def __init__(self, value, **kargs):
        super(CreateWindowFailed, self).__init__(value, **kargs)
    
class ButtonDisabled(sikulifwException):
    def __init__(self, value, **kargs):
        super(ButtonDisabled, self).__init__(value, **kargs)