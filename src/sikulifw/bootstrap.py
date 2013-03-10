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
from sikuli.Sikuli import addImagePath, setShowActions, setAutoWaitTimeout, getNumberScreens
import shutil
from org.sikuli.script import OS
from sikulifw.config import Config
from sikulifw.tool import Tool
from log import *
from log.robotFramework import Logger as RobotLogger
from sikulifw.region import Transform
from sikulifw.region.finder import Finder
from sikulifw.entity import Entity, MultiResultProxy, Searcher
from sikulifw.error import sikulifwException
from sikulifw.region.transform import EntityTransform, RegionScreen
from sikulifw.entity.entities import ClickableEntity, Canvas
from sikulifw.entity.clickStrategy import StandardClick, ClickStrategy
from sikulifw.entity.canvas.drawingStrategy import SegmentDrawingStrategy
from sikulifw.launcher import Launcher
from sikulifw.log.formatter import Formatter
from sikulifw.wrapper import *
from sikuli.Screen import Screen

## Inject Dependencies

Logger.setRobotLogger(RobotLogger())
Logger.setFormatter(Formatter)

Config.setLogger(Logger)
Config.setScreenshotLoggingLevel(INFO)

sikulifwException.setConfig(Config)
sikulifwException.setLogger(Logger)
        
Entity.setLogger(Logger)
Entity.setRegionFinderStrategy(Finder)
Entity.setMultiResultProxyStrategy(MultiResultProxy)
Entity.setSearcherStrategy(Searcher)
Entity.setConfig(Config)

ClickableEntity.setDefaultClickStrategy(StandardClick())
ClickStrategy.setLogger(Logger)
ClickStrategy.setScreen(Config.screen)

Transform.setLogger(Logger)
RegionScreen.setConfig(Config)

Finder.setLogger(Logger)
Finder.setConfig(Config)
Finder.setTransform(Transform)

MultiResultProxy.setEntitySearcher(Searcher)

Formatter.setTool(Tool)
Formatter.setConfig(Config)

EntityTransform.setConfig(Config)

Canvas.setDefaultDrawingStrategy(SegmentDrawingStrategy)

Logger.getRobotLogger().debug("[sikulifw] booting.. SikuliVersion=%s" % Env.getSikuliVersion()) # added in rc-2

Launcher.setLogger(Logger)

# works on all platforms
slash = "\\" if Env.getOS() == OS.WINDOWS else "/"

#add image libraries (searched in order)
addImagePath(Config.imageBaseline + slash + "lang" + slash + Config.language + "_" + Config.locale + slash + "os" + slash + str(Env.getOS()).lower() + slash + str(Env.getOSVersion(True)).lower())
addImagePath(Config.imageBaseline + slash + "lang" + slash + Config.language + "_" + Config.locale + slash + "os" + slash + str(Env.getOS()).lower())
addImagePath(Config.imageBaseline + slash + "lang" + slash + Config.language + "_" + Config.locale)

addImagePath(Config.imageBaseline + slash + "lang" + slash + Config.language + slash + "os" + slash + str(Env.getOS()).lower() + slash + str(Env.getOSVersion(True)).lower())
addImagePath(Config.imageBaseline + slash + "lang" + slash + Config.language + slash + "os" + slash + str(Env.getOS()).lower())
addImagePath(Config.imageBaseline + slash + "lang" + slash + Config.language)

addImagePath(Config.imageBaseline + slash + "os" + slash + str(Env.getOS()).lower() + slash + str(Env.getOSVersion(True)).lower())
addImagePath(Config.imageBaseline + slash + "os" + slash + str(Env.getOS()).lower())
addImagePath(Config.imageBaseline)

# Cleanup previous runs
try:
    shutil.rmtree(Config.resultDir + Config.resultAssetDir ) # Delete results directory
except OSError, e:
    pass # Directory must have already been deleted

# Create result directory structure
os.makedirs(Config.resultDir + Config.resultAssetDir)

# setup dest directory for tools
Tool.setDestDir(Config.resultDir + Config.resultAssetDir)

# Sikuli shows a visual effect (a blinking double lined red circle) on the spot where the action
if Config.debugPlaybackMode: 
    setShowActions(True)

setAutoWaitTimeout(Config.waitTime)
Config.screen.setAutoWaitTimeout(Config.waitTime)
Region.timeout = Config.waitTime

# Set the logging level
if os.environ.get('LOGLEVEL') == 'INFO':
    Logger.getRobotLogger().setLevel(INFO)
elif os.environ.get('LOGLEVEL') == 'DEBUG':
    Logger.getRobotLogger().setLevel(DEBUG)
elif os.environ.get('LOGLEVEL') == 'TRACE':
    Logger.getRobotLogger().setLevel(TRACE)
else:
    Logger.getRobotLogger().setLevel(INFO)
    
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

Logger.getRobotLogger().debug(Config.toString())

