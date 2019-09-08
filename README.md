# DynamiteRankings

## Development Environment Setup

### Python 3

Download [here](https://www.python.org/downloads/).

The reference version used is 3.7.4.

#### Numpy

Numpy is likely install with Python by default, otherwise after Python installation, type:

    python -m pip install numpy

#### Pylint

Pylint is likely install with Python by default, otherwise after Python installation, type:

    python -m pip install pylint

### Visual Studio Code

Any IDE/debugger/terminal can be used, but Visual Studio Code is recommended if you have no prior preference.

Download [here](https://code.visualstudio.com/download).

#### Configure Python

Once Visual Studio Code is installed, tell Visual Studio Code which version of Python to use. Either open the Command Palette (`Ctrl+Shift+P`) and type "Python: Select Interpreter", or click the button on the bottom left that says "Select Python Environment". After setup, the same location in the bottom left should always be displaying your active Python version.

Find more detailed instructions [here](https://code.visualstudio.com/docs/python/environments).

#### Extensions

Once Visual Studio Code is installed, go to the Extensions tab on the left, and install the following Extensions for the best integration:

- Python (ms-python.python)
- (Optional) Excel Viewer (grapecity.gc-excelviewer) - no need to open .csv files in Excel
- (Optional) GitLens (eamodio.gitlens) - see who last changed a file and compare versions
- (Optional) markdownlint (davidanson.vscode-markdownlint) - get help writing .md files

## Program Execution and Debugging

Open the root project folder in Visual Studio Code (such that .env, LICENSE, README, etc. are in the top level). If you don't use Visual Studio Code for anything else, this folder will be reopened every time Visual Studio Code starts.

To run the program, either type the appropriate command in the Terminal window (View > Terminal):

    python rank.py 2019 3
    python predict.py 2018 bowl

Or configure the .vscode/launch.json file to set the appropriate year and week input arguments to run any of the preconfigured functions, or add your own. Click on the Debug tab on the left, and select which function to run in the drop down menu at the top (or click on the arrow icon on the bottom left toolbar). Click the green arrow or hit F5 to run that function. To debug the code in detail, set a breakpoint in any code file before running to pause the program there. Use the Variables window to inspect values, and the Debug Console (View > Debug Console) to run Python commands while paused.

### Updating TheKickIsBAD

TheKickIsBAD is configured as a git submodule, and downloads the new scores and stats externally to DynamiteRankings. Updating to the latest commit of TheKickIsBAD with the new files is all that is needed inside DynamiteRankings. To pull new commits in a submodule, change directory into TheKickIsBAD before executing the git pull command.

    # Pull changes from DynamiteRankings if necessary
    DynamiteRankings> git pull

    # Pull new scores/stats from TheKickIsBAD
    DynamiteRankings> cd TheKickIsBAD
    DynamiteRankings/TheKickIsBAD> git pull

    # Commit and push new scores/stats to DynamiteRankings
    DynamiteRankings/TheKickIsBAD> cd ..
    DynamiteRankings> git add TheKickIsBAD
    DynamiteRankings> git commit -m "update TKIB submodule for week N"
    DynamiteRankings> git push

At the beginning of a new season, TheKickIsBAD needs to be updated with a new teams and conferences file, a number_of_weeks file for the year, and a first pass of the seasons schedule downloaded via download_scores.
