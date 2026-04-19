*** Settings ***
Library    examples/robotframework/keywords/SikuliGoLibrary.py
Suite Setup    Open Screen
Suite Teardown    Close Screen

*** Test Cases ***
Click Pattern On Screen
    ${coords}=    Click Image    assets/pattern.png    timeout_millis=5000    exact=${TRUE}
    Log    Clicked at (${coords}[0], ${coords}[1])
