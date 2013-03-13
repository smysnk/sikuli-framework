
from log.robotFramework import Logger as RobotLogger
from log import *
from entity import Entity
from region.tests.mockFinder import Finder
from log.formatter import Formatter
from config import Config
from entity.searcher import Searcher
from tests.mockTool import Tool
import unittest
from entity.multiResultProxy import MultiResultProxy

Logger.setRobotLogger(RobotLogger())
Logger.setFormatter(Formatter)        

Formatter.setTool(Tool)
Formatter.setConfig(Config)

Entity.setLogger(Logger)
Entity.setRegionFinderStrategy(Finder)
Entity.setSearcherStrategy(Searcher)
Entity.setMultiResultProxyStrategy(MultiResultProxy)

MultiResultProxy.setEntitySearcher(Searcher)