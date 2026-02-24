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

import re
import inspect
from . import Entity, MultiResultProxy
from compat import text_type

class KeyNotFoundException(Exception):
    pass

class AmbiguousKeySearchException(Exception):
    pass


class SearchResult(object):
    entity = None
    parent = None
    owner = None
    
    def __init__(self, entity=None, parent=None, owner=None):
        self.setEntity(entity)
        self.setParent(parent)
        self.setOwner(owner)
    
    def setEntity(self, entity):
        self.entity = entity
    
    def getEntity(self):
        return self.entity
    
    def setParent(self, parent):
        self.parent = parent
        
    def getParent(self):
        return self.parent
        
    def setOwner(self, owner):
        self.owner = owner
        
    def getOwner(self):
        return self.owner
    
    def __str__(self):
        if self.owner:
            return "%s.%s parent=%s" % (self.owner, self.entity, self.parent)
        else:
            return "%s parent=%s" % (self.entity, self.parent)

class Searcher(object):
    """
    Core search engine of Entity/SubEntity searchByName functions.
    Was created so that RobotFramework keywords could interact with AppFramework using plain language.  
    """
    
    pool = None
    
    def __init__(self):
        super(Searcher, self).__init__()
        self.pool = []
    
    def add(self, container, parent=None):        
        """
        Add a Entity or MultiProxy to the search pool
        """
        
        if isinstance(container, MultiResultProxy):
            # Recursively call this function to add all classes in the proxy
            
            for result in container.getResults():
                                
                if isinstance(result, tuple): # This is a result that has a custom parent                                        
                    self.add(result[0], result[1]) # Recurse
                else:
                    
                    self.add(result) # Recurse    
        
        elif inspect.isclass(container):

            self.pool.append(SearchResult(entity=[container,], parent=parent)) # Add the class itself
                        
            for key in container.__dict__:
                
                # Ensure this member variable has a defined variable and is a list (All entity definitions will be lists)
                if container.__dict__[key] and isinstance(container.__dict__[key], list):
                    self.pool.append(SearchResult(owner=container, entity=container.__dict__[key], parent=parent))     

                             
        elif isinstance(container, object):
            # This is a class, add all the keys of this class
            
            self.pool.append(SearchResult(entity=[container,], parent=parent)) # Add the class itself
                        
            for key in container.__class__.__dict__:
                
                # Ensure this member variable has a defined variable and is a list (All entity definitions will be lists)
                if container.__class__.__dict__[key] and isinstance(container.__class__.__dict__[key], list):
                    self.pool.append(SearchResult(owner=container, entity=container.__class__.__dict__[key], parent=parent))     
                

    def search(self, query):
        """
        Given space separated search terms, will return an entity definition that most closely matches.
        Implements a strategy of returning entities that have the smallest number of words. This will allow for the 
        client to be more specific if ambiguity arises.
        """
            
        if isinstance(query, text_type):
            return self.searchWithString(str(query))
        elif isinstance(query, tuple):
            # Member variable search 
            return self.searchWithClassOrMemberVariable(query)
        elif isinstance(query, object):
            # Class
            return self.searchWithClassOrMemberVariable(query)
        else:
            raise Exception("Not sure how to handle query type, query=%s" % query)
        
        
    def searchWithClassOrMemberVariable(self, query):
        
        results = []
        
        # Go through all pool items and see if any of our entities match the query
        for poolItem in self.pool:             
            if (isinstance(query, object) and poolItem.getEntity() == [query]) or poolItem.getEntity() == query:
                results.append(poolItem)
                    
        if len(results) == 0:         

            # Convert items to string so they can be used in join in the exception
            poolItems = []
            for poolItem in self.pool:
                poolItems.append(str(poolItem))                  
            
            raise KeyNotFoundException("Unable to find class for key=%s in:\n%s" % (query, '\n'.join(poolItems)))
        elif len(results) > 1:
            raise AmbiguousKeySearchException("Multiple classes for key=%s classes=%s" % (query, results))
        else:
            return results[0]
    
    def searchWithString(self, query):
        
        foundKeys = {}
        
        # Get the search words used to find the target element 
        searchWords = str.lower(query).split(' ')
        
        # Go through all the keys and find somethin!
        for poolItem in self.pool:
            
            if isinstance(poolItem.getEntity()[0], str):
                curEntityName = poolItem.getEntity()[0]
            elif inspect.isclass(poolItem.getEntity()[0]):
                curEntityName = poolItem.getEntity()[0].__name__
            elif isinstance(poolItem.getEntity()[0], Entity):
                curEntityName = poolItem.getEntity()[0].getName()
            
            else:
                raise Exception("Unable to get entity name")
                            
            # Find at the words in the current entity name
            entityWords = re.findall("(?m)((?:[A-Z0-9]{1}|^[a-z]{1})[a-z]*)", curEntityName)
            
            # Convet words to lower case
            for index, word in enumerate(entityWords):
                entityWords[index] = str.lower(word)
                

            # Make sure all our search words matched
            intersect =  list(set(searchWords) & set(entityWords))
            if intersect and len(intersect) == len(searchWords):
                
                # Create a list of keys matched, and number of words they have
                entityWordCount = len(entityWords)
                if foundKeys.get(entityWordCount):
                    foundKeys[entityWordCount].append(poolItem)
                else:
                    foundKeys[entityWordCount] = [poolItem]
                        
                                        
        if len(foundKeys) == 0:
            
            # Convert items to string so they can be used in join in the exception
            poolItems = []
            for poolItem in self.pool:
                poolItems.append(str(poolItem))                
                
            raise KeyNotFoundException("Unable to find [%s] in:\n%s" % (query, "\n".join(poolItems)))
    
        # Return the match with the least number of words (it will be more specific)
        for wordsMatchedIndex, matches in sorted(foundKeys.items()):
            
            if len(matches) > 1:          
                raise AmbiguousKeySearchException("Target [%s] is ambiguous, matches=%s" % (query, matches))
            else:
                return matches[0]    
            
