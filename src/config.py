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

import os

BACKEND_LEGACY = "legacy"
BACKEND_SIKULIGO = "sikuligo"
_SELECTED_BACKEND = os.environ.get("SIKULI_FRAMEWORK_BACKEND", BACKEND_LEGACY).strip().lower()


def _noop(*args, **kwargs):
    return None


if _SELECTED_BACKEND == BACKEND_SIKULIGO:
    from adapters.sikuligo_backend import Screen

    setShowActions = _noop

    def getNumberScreens():
        return 1

    class _Settings(object):
        MoveMouseDelay = 0
        SlowMotionDelay = 0
        DelayAfterDrag = 0
        DelayBeforeDrop = 0
        MinSimilarity = 0.8
        ObserveScanRate = 0.5
        WaitScanRate = 1

    Settings = _Settings

    class _Thread(object):
        @staticmethod
        def currentThread():
            return None

    Thread = _Thread
    JRegion = None
else:
    from sikuli.Sikuli import setShowActions, getNumberScreens
    from org.sikuli.basics import Settings
    from java.lang import Thread
    from sikuli import Env, Screen
    from org.sikuli.script import Region as JRegion

# http://sikuli.org/docx/globals.html#Settings.MinSimilarity
Settings.MoveMouseDelay = 0
Settings.SlowMotionDelay = 0
Settings.DelayAfterDrag = 0
Settings.DelayBeforeDrop = 0
Settings.MinSimilarity = 0.8      # The default minimum similiarty of find operations. While using a Region.find() operation, if only an image file is provided, Sikuli searches the region using a default minimum similarity of 0.7.
Settings.ObserveScanRate = 0.5      # http://sikuli.org/docx/globals.html#Settings.ObserveScanRate
Settings.WaitScanRate = 1

class Config():
    backend = _SELECTED_BACKEND
    
    highlightTime = 1  # When debugging is enabled.. highlight exists, wait, etc    
    waitTime = 0
    
    imageBaseline = "resources/baseline" # image baseline directory    
    
    loggingLevel = None # If 'development' file exists in root, we're in dev env
    screenshotLoggingLevel = None
    
    debugPlaybackMode = False #debugPlaybackMode = True if os.path.isfile('development') else False

    resultDir = "results/"
    resultAssetDir = "assets/"
    imageSuffix = ".png"
    imageSearchPaths = []
    screen = None
    
    language = "en"
    locale = "CA"
    captureBaseline = False
    
    regionTimeout = 3
    
    # Initialize the logger and set the logging level
    logger = None #log.Logger(level=loggingLevel) - move to bootstrap
    
    mainThread = Thread.currentThread() 

    @classmethod
    def initScreen(cls):
        if cls.screen is not None:
            return cls.screen
        if cls.backend == BACKEND_SIKULIGO:
            cls.screen = Screen.auto()
        else:
            cls.screen = Screen(0)
        return cls.screen

    @classmethod
    def setScreen(cls, screen):
        cls.screen = screen

    @classmethod
    def setImageSearchPaths(cls, paths):
        cls.imageSearchPaths = list(paths)

    @classmethod
    def getImageSearchPaths(cls):
        if cls.imageSearchPaths:
            return list(cls.imageSearchPaths)
        return [cls.imageBaseline]
    
    @classmethod
    def setRegionTimeout(cls, timeout):
        cls.regionTimeout = timeout
        if JRegion is not None:
            JRegion.timeout = Config.regionTimeout
    
    @classmethod
    def setLogger(cls, logger):
        cls.logger = logger
    
    @classmethod
    def getLogger(cls):
        return cls.logger
            
    @classmethod
    def getLoggingLevel(cls):
        return cls.logger.getLoggingLevel()
    
    @classmethod
    def getScreen(cls):
        return cls.initScreen()
    
    @classmethod
    def setScreenshotLoggingLevel(cls, level):
        
        cls.logger.getLogger().log(level, "Changing screenshot logging level")
        cls.screenshotLoggingLevel = level
        
    @classmethod
    def getScreenshotLoggingLevel(cls):
        return cls.screenshotLoggingLevel
    
    @classmethod
    def toString(cls):
        
        str = "Highlight time=%d\n" % cls.highlightTime
        str = str + "waitTime=%d\n" % cls.waitTime
        str = str + "backend=%s\n" % cls.backend
        str = str + "screen=%s (available=%d)\n" % (cls.screen, getNumberScreens())
        str = str + "regionTimeout=%d\n" % cls.regionTimeout
        str = str + "logLevel=%s\n" % cls.loggingLevel
        str = str + "screenshotLogLevel=%s\n" % cls.screenshotLoggingLevel
        
        return str
