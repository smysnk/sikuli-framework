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
import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[2] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import bootstrap
from config import Config
from log import EntityLoggerProxy
from log.level import TRACE
from maps.textedit import TextEdit, MenuBar, FileMenu, TextEditMenu
from region.transform import RegionMorph
from launcher import Launcher

"""
Simple example that validates that the calculator is present on the screen.
This example does not use the Launcher() class so it assumes that the application
is already running.  Results can be found in the /results directory. 
"""

# Change logging level verbosity
#EntityLoggerProxy.getLogger().setLevel(TRACE)
Config.setScreenshotLoggingLevel(TRACE)


# Launch the Calculator binary
textedit = Launcher.run('TextEdit')
logger = EntityLoggerProxy(textedit)

# Type some text in the text area
textedit[TextEdit.TEXT_AREA].type("This is a demo of SikuliFramework")

# Resize the application size 4 times
for i in range(0,4):
    
    # Get the current application region
    region = textedit.validate().region
    
    # Alternate between growing / shrinking application width
    offset = 100 * (1 - ((i % 2)*2))
    
    # Modify the size of current application region
    morph = RegionMorph(0, 0, offset, 0)
    region = morph.apply(region) 
    region = region.right(0).below(0) # Get the bottom right corner
    
    logger.info("resizing bottom right corner to %s" % region)
    
    # Drag the bottom right hand corner 100px to right
    textedit[TextEdit.BOTTOM_RIGHT_CORNER].drag(region)

# Close down the application
textedit[TextEdit.MENU_BAR][MenuBar.TEXTEDIT].click() \
    [TextEditMenu.QUIT].click()
