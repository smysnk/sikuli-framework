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

import inspect

class MultiResultProxy(object):
    """
    When the result of clicking an entity has more than one outcomes this proxy class is used to support all of them.
    It helps us lazy load the desired outcome specified by the client.
    """
    
    parent = None
    results = None
    resultArgs = {}
    caller = None
    entitySeacher = None
    
    @classmethod
    def setEntitySearcher(cls, entitySearcher):
        cls.entitySeacher = entitySearcher
    
    def __init__(self, parent, results, caller):
        
        self.parent = parent
    
        assert isinstance(results, list)            
        self.setResults(results)
        self.caller = caller
        
        self.searcher = self.entitySeacher()
        self.searcher.add(self)
    
    
    def __getitem__(self, key):
        """ 
        Initiate class based on which key is supplied 
        Eg. key = WindowEntity.KEY
            
        2) Initiate the Window
        
        """
        
        searchResult = self.searcher.search(key)
        
        if inspect.isfunction(searchResult.getParent()):
            parent = searchResult.getParent()(self.parent)
        elif searchResult.getParent():
            parent =  searchResult.getParent() 
        else:
            parent = self.parent
        
        try:
            # Try the key as a member variable
            
            owner = searchResult.getOwner()(parent, caller=self, **self.resultArgs)
            return owner[searchResult.getEntity()]
        
        except TypeError:
            # Key was a class
            
            return searchResult.getEntity()[0](parent, caller=self, **self.resultArgs)
        
        finally:
            pass
        
    def setResults(self, results):
        
        self.results = []
        
        # Allow for lambda parents, we need to evaluate them before they can be searched
        for result in results:            
            # Evaluate lambda's
            if isinstance(result, tuple) and inspect.isfunction(result[0]):
                result = (result[0](),result[1])
                                                        
            self.results.append(result)
        
    
    def getResults(self):
        return self.results
    
    def setResultArgs(self, args):
        
        self.resultArgs = args        
            
