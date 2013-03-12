SikuliFramework - GUI Automation Framework for Sikuli
================

SikuliFramework provides an object-oriented abstraction on top of [Sikuli](http://www.sikuli.org) to assist with interacting GUI elements, such as sets of buttons, checkboxes, radio buttons, windows and dialogue hierarchies for GUI automation and testing.  

## Common problems with traditional "Sikuli scripts"

Most traditional "Sikuli scripts" are created by capturing baseline images around a series of steps required to solve a particular problem.  This allows for the quick creation of a script to solve a problem.  There are however a few inherent problems with creating scripts in this method, these include:

  - Maintainability issues
     - Baseline images are usually very specific to a test and cannot be reused
     - If the any of the baseline images change, multiple baseline images need be fixed for 1 change in the UI 
     - No enforced naming convention for baseline pictures (Everyone has a different way of naming things)
  - [Fragile tests](http://xunitpatterns.com/Fragile%20Test.html)
     - "Sikuli script" often devolve into "hacky" code to get the job done, but it is hard to create truly maintainable tests
        - Use of wait(seconds) function depends on computer being fairly fast or increased time is needed, lots of time is wasted waiting around, decreases the readability of tests if there are wait commands everywhere
        - Operations are performed without validating whether the system is actually in sync
            - Clicking a checkbox, is the checkbox actually selected after the operation?
            - Entering text, is the text entered as you expect it?
            - Did clicking a button actually perform the action you expected it to? A regular Sikuli script will only fail after it cannot find an image it is expecting to present on the screen

**SikuliFramework** was created to solve some of the complexities and also offers the following benefits:

 - Cleaner, more readable code
 - Provides structure to the naming of baseline images
 - Dynamic resolution of image assets (Designate different images based on OS)
 - Encourages baseline reuse (Rather than capturing images to solve your immediate task, capture to solve all tasks)
 - Higher accuracy matching GUI components due to use of Regions
 - Tight integration with [RobotFramework](http://code.google.com/p/robotframework/) - Inspired by [Mike's cognition's Blog](http://blog.mykhailo.com/2011/02/how-to-sikuli-and-robot-framework.html) 
 - Encourages code reuse in RobotFramework test libraries
 - Streamlines baseline creation for assertions (baselines are created automatically during the initial run of the script)
 - Solves some of Sikuli's common downfalls (false-positives, context issues)
 - Greatly improved reports for debugging and general-purpose
 - Increases the robustness of test scripts (less dependant on speed of the machine, resolution, other problems)

## Code Examples

### Example 1 - Validating Calculator is present on the screen

#### (Python) - #python run.py quickstart/calculator/validate.py

    calculator = Calculator()
	calculator.validate()

### Example 2 - Adding 2 + 2 (OSX/Win)

#### (Python) - #python run.py quickstart/calculator/add.py

    calculator = Launcher.run("Calculator")
    calculator[Calculator.BUTTON_2].click() \
        [Calculator.BUTTON_PLUS].click() \
        [Calculator.BUTTON_2].click() \
        [Calculator.BUTTON_EQUALS].click()
  
    calculator[Calculator.SCREEN].assertEquals("4")

#### (RobotFramework TSV) - #python run.py quickstart/calculator/add.tsv
    
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

### Example 3 - Convert 25 celsius to fahrenheit (OSX) - #python run.py quickstart/calculator/convert.py

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
    
    


    
    
    
    
    
