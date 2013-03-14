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
from sikuli import Env
from sikuli.Sikuli import getImagePath, addImagePath, setShowActions, setAutoWaitTimeout, getNumberScreens
import shutil
from org.sikuli.script import OS
from config import Config
from tool import Tool
from log import *
from region import Transform
from region.finder import Finder
from entity import Entity, MultiResultProxy, Searcher
from error import SikuliFrameworkException
from region.transform import EntityTransform, RegionScreen
from entity.entities import ClickableEntity, Canvas
from entity.clickStrategy import StandardClick, ClickStrategy
from entity.canvas.drawingStrategy import SegmentDrawingStrategy
from launcher import Launcher
from log.formatter import Formatter
from wrapper import *
from sikuli.Screen import Screen
import __main__

# Detect where the script is being executed from
try:
    # Set the baseline directory to be relative to the main script file
    Config.imageBaseline = "%s/baseline" % os.path.dirname(__main__.__file__)
except AttributeError, e:
    # We might be running from RobotFramework
    from robot.libraries.BuiltIn import BuiltIn
    Config.imageBaseline = "%s/baseline" % os.path.dirname(BuiltIn().replace_variables('${SUITE SOURCE}'))

# Cleanup previous runs
try:
    shutil.rmtree(Config.resultDir) # Delete results directory
except OSError, e:
    pass # Directory must have already been deleted

# Create result directory structure
os.makedirs(Config.resultDir + Config.resultAssetDir)

# setup dest directory for tools
Tool.setDestDir(Config.resultDir + Config.resultAssetDir)

## Inject Dependencies
EntityLoggerProxy.setLogger(Logger())
EntityLoggerProxy.setFormatter(Formatter)

Config.setLogger(EntityLoggerProxy)
Config.setScreenshotLoggingLevel(INFO)

SikuliFrameworkException.setConfig(Config)
SikuliFrameworkException.setLogger(EntityLoggerProxy)
        
Entity.setLogger(EntityLoggerProxy)
Entity.setRegionFinderStrategy(Finder)
Entity.setMultiResultProxyStrategy(MultiResultProxy)
Entity.setSearcherStrategy(Searcher)
Entity.setConfig(Config)

ClickableEntity.setDefaultClickStrategy(StandardClick())
ClickStrategy.setLogger(EntityLoggerProxy)
ClickStrategy.setScreen(Config.screen)

Transform.setLogger(EntityLoggerProxy)
RegionScreen.setConfig(Config)

Finder.setLogger(EntityLoggerProxy)
Finder.setConfig(Config)
Finder.setTransform(Transform)

MultiResultProxy.setEntitySearcher(Searcher)

Formatter.setTool(Tool)
Formatter.setConfig(Config)

EntityTransform.setConfig(Config)

Canvas.setDefaultDrawingStrategy(SegmentDrawingStrategy)

Launcher.setLogger(EntityLoggerProxy)


## Boot

logger = EntityLoggerProxy()
logger.info("[SikuliFramework] Booting.. SikuliVersion=%s" % Env.getSikuliVersion())

# Works on all platforms
slash = "\\" if Env.getOS() == OS.WINDOWS else "/"

# Add image libraries (searched in order)
addImagePath(Config.imageBaseline + slash + "os" + slash + str(Env.getOS()).lower() + slash + str(Env.getOSVersion(True)).lower() + slash + Config.language )
addImagePath(Config.imageBaseline + slash + "os" + slash + str(Env.getOS()).lower() + slash + str(Env.getOSVersion(True)).lower())

addImagePath(Config.imageBaseline + slash + "os" + slash + str(Env.getOS()).lower() + slash + Config.language )
addImagePath(Config.imageBaseline + slash + "os" + slash + str(Env.getOS()).lower())

addImagePath(Config.imageBaseline + slash + Config.language )
addImagePath(Config.imageBaseline)

logger.trace("Image search path: %s" % getImagePath())

# Sikuli shows a visual effect (a blinking double lined red circle) on the spot where the action
if Config.debugPlaybackMode: 
    setShowActions(True)

setAutoWaitTimeout(Config.waitTime)
Config.screen.setAutoWaitTimeout(Config.waitTime)
Region.timeout = Config.waitTime

# Set the logging level
if os.environ.get('LOGLEVEL') == 'INFO':
    EntityLoggerProxy.getLogger().setLevel(INFO)
elif os.environ.get('LOGLEVEL') == 'DEBUG':
    EntityLoggerProxy.getLogger().setLevel(DEBUG)
elif os.environ.get('LOGLEVEL') == 'TRACE':
    EntityLoggerProxy.getLogger().setLevel(TRACE)
else:
    EntityLoggerProxy.getLogger().setLevel(INFO)
    
# Set the screenshot logging level
if os.environ.get('LOGLEVEL_SCREENSHOTS') == 'INFO':
    Config.setScreenshotLoggingLevel(INFO)
elif os.environ.get('LOGLEVEL_SCREENSHOTS') == 'DEBUG':
    Config.setScreenshotLoggingLevel(DEBUG)
elif os.environ.get('LOGLEVEL_SCREENSHOTS') == 'TRACE':
    Config.setScreenshotLoggingLevel(TRACE)

# Set default timeout
Config.setRegionTimeout(Config.regionTimeout)


# Setup our wrapped functions
Screen.debugPlaybackMode = Config.debugPlaybackMode
Screen.highlightTime = Config.highlightTime
Region.debugPlaybackMode = Config.debugPlaybackMode
Region.highlightTime = Config.highlightTime

logger.debug(Config.toString())

