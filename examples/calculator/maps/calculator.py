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

from entity import Window, Button, TextBox, DropDown, Application,\
    CheckBox, Radio, ProgressBar
from org.sikuli.script import OS

        
class Calculator(Application):
    
    shared_state = {}

    LCD_DISPLAY = ["lcdDisplay", TextBox]
    BUTTON_0 = ["buttonZero", Button]
    BUTTON_1 = ["buttonOne", Button]
    BUTTON_2 = ["buttonTwo", Button]
    BUTTON_3 = ["buttonThree", Button]
    BUTTON_4 = ["buttonFour", Button]
    BUTTON_5 = ["buttonFive", Button]
    BUTTON_6 = ["buttonSix", Button]
    BUTTON_7 = ["buttonSeven", Button]
    BUTTON_8 = ["buttonEight", Button]
    BUTTON_9 = ["buttonNine", Button]
    BUTTON_DECIMAL = ["buttonDecimal", Button]
    BUTTON_EQUALS = ["buttonEquals", Button]
    BUTTON_PLUS = ["buttonPlus", Button]
    BUTTON_MINUS = ["buttonMinus", Button]
    BUTTON_MULTIPLY = ["buttonMultiply", Button]
    BUTTON_NEGATE = ["buttonNegate", Button]
    BUTTON_DIVIDE = ["buttonDivide", Button]
    BUTTON_CLEAR = ["buttonClear", Button]
    BUTTON_MEMORY_CLEAR = ["buttonMemoryClear", Button]
    BUTTON_MEMORY_ADD = ["buttonMemoryAdd", Button]
    BUTTON_MEMORY_SUBTRACT = ["buttonMemorySubtract", Button]
    BUTTON_MEMORY_RECALL = ["buttonMemoryRecall", Button]

    def __init__(self):
        super(Calculator, self).__init__()

        self.binary[OS.WINDOWS] = 'calc.exe'
        self.binary[OS.MAC] = 'open /Applications/Calculator.app'
    