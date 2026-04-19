"""
Runtime bootstrap for the SikuliGO-backed framework.
"""

from __future__ import annotations

import __main__
import os
import shutil

from config import Config, setShowActions
from entity import Entity, MultiResultProxy, Searcher
from entity.canvas.drawingStrategy import SegmentDrawingStrategy
from entity.clickStrategy import ClickStrategy, StandardClick
from entity.entities import Canvas, ClickableEntity
from error import SikuliFrameworkException
from launcher import Launcher
from log import DEBUG, INFO, TRACE, EntityLoggerProxy, Logger
from log.formatter import Formatter
from region import Transform
from region.finder import Finder
from region.transform import EntityTransform, RegionScreen
from tool import Tool
from wrapper import Env, Region, Screen


def _detect_baseline_root() -> str:
    try:
        return os.path.join(os.path.dirname(__main__.__file__), "baseline")
    except AttributeError:
        from robot.libraries.BuiltIn import BuiltIn

        suite_source = BuiltIn().replace_variables("${SUITE SOURCE}")
        return os.path.join(os.path.dirname(suite_source), "baseline")


def _build_image_search_paths(image_baseline: str) -> list[str]:
    os_name = str(Env.getOS()).lower()
    os_version = str(Env.getOSVersion(True)).lower()
    language = str(Config.language).lower()

    paths = []
    if os_name:
        if os_version:
            paths.append(os.path.join(image_baseline, "os", os_name, os_version, language))
            paths.append(os.path.join(image_baseline, "os", os_name, os_version))
        paths.append(os.path.join(image_baseline, "os", os_name, language))
        paths.append(os.path.join(image_baseline, "os", os_name))
    paths.append(os.path.join(image_baseline, language))
    paths.append(image_baseline)
    return paths


Config.imageBaseline = _detect_baseline_root()
Config.setImageSearchPaths(_build_image_search_paths(Config.imageBaseline))

shutil.rmtree(Config.resultDir, ignore_errors=True)
os.makedirs(os.path.join(Config.resultDir, Config.resultAssetDir), exist_ok=True)

Tool.setDestDir(os.path.join(Config.resultDir, Config.resultAssetDir))

EntityLoggerProxy.setLogger(Logger())
EntityLoggerProxy.setFormatter(Formatter)

Config.setLogger(EntityLoggerProxy)
Config.setScreenshotLoggingLevel(INFO)
Config.initScreen()

SikuliFrameworkException.setConfig(Config)
SikuliFrameworkException.setLogger(EntityLoggerProxy)

Entity.setLogger(EntityLoggerProxy)
Entity.setRegionFinderStrategy(Finder)
Entity.setMultiResultProxyStrategy(MultiResultProxy)
Entity.setSearcherStrategy(Searcher)
Entity.setConfig(Config)

ClickableEntity.setDefaultClickStrategy(StandardClick())
ClickStrategy.setLogger(EntityLoggerProxy)
ClickStrategy.setScreen(Config.getScreen())

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

logger = EntityLoggerProxy()
logger.info(
    "[SikuliFramework] Booting.. backend=%s SikuliVersion=%s"
    % (Config.backend, Env.getSikuliVersion())
)
logger.trace("Image search path: %s" % Config.getImageSearchPaths())

if Config.debugPlaybackMode:
    setShowActions(True)

Config.getScreen().setAutoWaitTimeout(Config.waitTime)

if os.environ.get("LOGLEVEL") == "INFO":
    EntityLoggerProxy.getLogger().setLevel(INFO)
elif os.environ.get("LOGLEVEL") == "DEBUG":
    EntityLoggerProxy.getLogger().setLevel(DEBUG)
elif os.environ.get("LOGLEVEL") == "TRACE":
    EntityLoggerProxy.getLogger().setLevel(TRACE)
else:
    EntityLoggerProxy.getLogger().setLevel(INFO)

if os.environ.get("LOGLEVEL_SCREENSHOTS") == "INFO":
    Config.setScreenshotLoggingLevel(INFO)
elif os.environ.get("LOGLEVEL_SCREENSHOTS") == "DEBUG":
    Config.setScreenshotLoggingLevel(DEBUG)
elif os.environ.get("LOGLEVEL_SCREENSHOTS") == "TRACE":
    Config.setScreenshotLoggingLevel(TRACE)

Config.setRegionTimeout(Config.regionTimeout)

Screen.debugPlaybackMode = Config.debugPlaybackMode
Screen.highlightTime = Config.highlightTime
Region.debugPlaybackMode = Config.debugPlaybackMode
Region.highlightTime = Config.highlightTime

logger.debug(Config.toString())
