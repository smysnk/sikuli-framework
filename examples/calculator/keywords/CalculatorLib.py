import bootstrap
from launcher import Launcher
import os, sys
from keywords.rfSikuliFwLib import RfSikuliFwLib
from org.sikuli.script import OS
from keywords.robotremoteserver import RobotRemoteServer
from maps.calculator import Calculator

class CalculatorLib(RfSikuliFwLib):

    def find(self):
        if not self.entity:
            self.create()
        
        self.entity.validate()
    
    def create(self):
        self.entity = Calculator()
    
    def launch(self):
        self.entity = Launcher.run('Calculator')
    
if __name__ == "__main__":
    
    RobotRemoteServer(NotebookLib(), *sys.argv[1:])

    