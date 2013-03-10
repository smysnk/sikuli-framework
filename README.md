SikuliFramework - Object-Oriented GUI Automation Framework 
================

SikuliFramework provides an object-oriented abstraction on top of [Sikuli](http://www.sikuli.org) to assist with interacting GUI elements, such as sets of buttons, checkboxes, radio buttons, windows and dialogue hierarchies for GUI automation and testing.  This abstraction also provides some of the following benefits:

 - Cleaner, more readable code
 - Provides structure to naming of image assets
 - Dynamic resolution of image assets (Designate different images based on OS)
 - Higher accuracy matching GUI components due to use of Regions
 - Tight integration with [RobotFramework](http://code.google.com/p/robotframework/) - Inspired by [Mike's cognition's Blog](http://blog.mykhailo.com/2011/02/how-to-sikuli-and-robot-framework.html) 

### Example 1 - Adding 2 + 2 on Calculator (OSX/Win)

#### (Python)

    calculator = Launcher.run("Calculator")
    calculator[Calculator.TWO].click()
              [Calculator.PLUS].click()
              [Calculator.TWO].click()
              [Calculator.EQUALS].click()
  
    calculator[Calculator.SCREEN].assertEquals("4")

#### (RobotFramework TSV)
    
    *Setting*
    Library	keywords/CalculatorLib.py	WITH NAME	Calculator

    *Test Case*
    Add Two Numbers
        Calculator.Launch
        Calculator.Click         Two
        Calculator.Click         Plus
        Calculator.Click         Two
        Calculator.Click         Equals
        ${Screen}=               Calculator.Select   Screen
		Calculator.AssertEquals	 ${Screen}           4

### Example 2 - Convert 25 celsius to fahrenheit (OSX)

    calculator = Launcher.run("Calculator")
    
    calculator[Calculator.SCREEN].type("25")
    
    # Select convert temperature from conversion menu
    convertDialog = calculator[Calculator.MENUBAR][MenuBar.CONVERT].click()
            [ConvertMenu.TEMPERATURE].click()
    
    # Change convert from celsius to fahrenheit
    convertDialog[ConvertDialog.FROM].click()
            [ConvertFromDropDown.CELSIUS].click()
            
    convertDialog[ConvertDialog.TO].click()
    		[ConvertToDropDown.FAHRENHEIT].click()
    		
    # Convert
    convertDialog[ConvertDialog.CONVERT].click()
    
    calculator[Calculator.SCREEN].assertEquals("77")
    
    


    
    
    
    
    
