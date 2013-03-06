
from sikulifw.log.robotFramework import Logger as RobotLogger
from sikulifw.log import *
from sikulifw.entity import Entity
from sikulifw.region.tests.mockFinder import Finder
from sikulifw.log.formatter import Formatter
from sikulifw.config import Config
from sikulifw.entity.searcher import Searcher
from sikulifw.tests.mockTool import Tool
import unittest
from sikulifw.entity.multiResultProxy import MultiResultProxy

Logger.setRobotLogger(RobotLogger())
Logger.setFormatter(Formatter)        

Formatter.setTool(Tool)
Formatter.setConfig(Config)

Entity.setLogger(Logger)
Entity.setRegionFinderStrategy(Finder)
Entity.setSearcherStrategy(Searcher)
Entity.setMultiResultProxyStrategy(MultiResultProxy)

MultiResultProxy.setEntitySearcher(Searcher)