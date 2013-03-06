import sikulifw.bootstrap
from maps.calculator.calculator import Calculator
from sikulifw.config import Config
from sikulifw.log import Logger
from sikulifw.log.level import TRACE

Logger.getRobotLogger().setLevel(TRACE)


calc = Calculator()
calc.validate()
