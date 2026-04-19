# SikuliFramework - GUI Automation Framework for Sikuli [![Tests](https://img.shields.io/github/actions/workflow/status/smysnk/Sikuli-go/go-test.yml?branch=master&label=tests)](https://github.com/smysnk/sikuli-go/actions/workflows/go-test.yml) [![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://github.com/smysnk/sikuli-go/blob/master/sikuli-framework/pyproject.toml) [![Backend sikuligo](https://img.shields.io/badge/backend-sikuligo-0a7ea4)](https://github.com/smysnk/sikuli-go/blob/master/sikuli-framework/docs/sikuligo-cutover-implementation-plan.md)

SikuliFramework provides an object-oriented abstraction on top of [Sikuli-go](https://smysnk.github.io/sikuli-go/) to assist with interacting GUI elements, such as sets of buttons, checkboxes, radio buttons, windows and dialogue hierarchies for GUI automation and testing.  

> Note: SikuliFramework now uses [Sikuli-go](https://github.com/smysnk/sikuli-go) as its implementation engine.

## What is Sikuli-go?

Sikuli-go is the underlying automation API used by this framework. It provides image-based GUI automation capabilities over a local API process, while `sikuli-framework` provides higher-level page/object style abstractions, reusable entities, and Robot Framework-friendly keywords on top of it.

Sikuli-go is a Go port of core SikuliX automation concepts and workflows. In practice, this means you keep the familiar image-driven automation model from SikuliX while using a modern Go-based backend API and Python client integrations.

## Quickstart

```bash
python -m pip install --upgrade pip
python -m pip install sikuli-go
cd sikuli-framework
python -m pytest -q tests/test_sample_map_integration.py -m integration
```

### Calculator example script

```bash
cd sikuli-framework/examples/calculator
python validate.py
python add.py
```

### TextEdit example script

```bash
cd sikuli-framework/examples/textedit
python resize.py
```

### Robot Framework example run

```bash
cd sikuli-framework
python -m pip install "robotframework>=7.0.0"
./robot-runner.sh examples/robotframework/click.robot
```

## Code Examples

#### Robot Framework script + output

    *Setting*
    Library	keywords/CalculatorLib.py	WITH NAME	Calculator

    *Test Case*
    Add Two Numbers
        Calculator.Launch
        Calculator.Click         Two
        Calculator.Click         Plus
        Calculator.Click         Two
        Calculator.Click         Equals
        ${Screen}=               Calculator.Select   Display
		Calculator.AssertEquals	 ${Display}           4

![RobotFramework Results Log](https://github.com/smysnk/sikuli-framework/raw/master/docs/images/robo_example.png)

![RobotFramework Results Log Hyperlinking](https://github.com/smysnk/sikuli-framework/raw/master/docs/images/robo_log_hyperlink.png)

#### Python API examples

    calculator = Calculator()

    # Chain together operations on the same window 
    calculator[Calculator.BUTTON_2].click()
        [Calculator.BUTTON_PLUS].click()
        [Calculator.BUTTON_2].click() 
        [Calculator.BUTTON_EQUALS].click()
        
    # Built-in assertions methods for testing purposes
    calculator[Calculator.SCREEN].assertEquals("4")

#### Map out special GUI elements such as a TextBox, Radio, Checkbox + more and interact with them as such

    calculator[Calculator.SCREEN].type("25")
    
#### Map out the resulting actions of clicking a button
    
    # Create initial application context
    textedit = TextEdit()
    
    # Result of clicking the TextEdit button is a TextEditMenu
    textEditMenu = textedit[TextEdit.MENU_BAR][MenuBar.TEXTEDIT].click()
    
    # Perform actions on the new context created from the result of the previous action
    textEditMenu[TextEditMenu.QUIT].click()

## Common problems with traditional "Sikuli scripts"

Traditional Sikuli scripts are often built by capturing screenshots for each step in a flow. This is fast to start, but it creates long-term maintenance and reliability issues.

- Hard to maintain:
  - Screenshots are often specific to one test and hard to reuse.
  - A small UI change can break multiple screenshots.
  - Image naming is usually inconsistent across teams.
- Fragile execution:
  - Scripts often rely on fixed waits (`wait(seconds)`), which are sensitive to machine speed.
  - Actions are executed without always validating application state first.
  - Failures are often discovered late, only when a later image cannot be found.
- Low signal diagnostics:
  - Failures can be difficult to debug without structured context and richer logs.

**SikuliFramework** addresses these issues and provides:

- Clearer, more maintainable automation code.
- Structured conventions for baseline image naming and organization.
- Reusable baseline assets across tests and workflows.
- OS-aware image resolution for cross-platform execution.
- Region-based interaction patterns to improve targeting accuracy.
- Robot Framework-friendly libraries and reusable keyword patterns.
- Better assertion and reporting workflows, including screenshot-based evidence.
- More robust scripts that are less sensitive to timing and environment differences.

**What is Sikuli?**

Sikuli is a visual technology to automate and test graphical user interfaces (GUI) using images (screenshots) of the software under test.
- [Wikipedia](http://en.wikipedia.org/wiki/Sikuli)

## Build and test workflows

See `BUILD.md` for:

- unit test commands
- integration test commands
- manual `sikuligo` server mode

## Legacy Docs

- Historical wiki: [Documentation + Tutorials](https://github.com/smysnk/sikuli-framework/wiki)
 
--------------------------------------

Created by Joshua Bellamy
    
    
    
