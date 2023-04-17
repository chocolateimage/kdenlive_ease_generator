# Kdenlive ease generator

## Tutorial
[![image](https://user-images.githubusercontent.com/95003834/232554753-3cdaf3b1-ccf3-4f2f-9245-c556973f1851.png)](https://youtu.be/1c1yGZ14XYo)

## Install
* Download the zip or clone the folder to the location of your choice on your computer.
* After extracting, follow the instructions below for your operating system.

### Windows

* Install Python from https://www.python.org/downloads/ if you haven't already
* In the installation, make sure to select "Add Python 3.XX to PATH"
* In this folder do: `pip install -r requirements.txt`

Tip: you can run the Python command by opening the folder in the File Explorer, then typing `cmd` in the address bar to open the command line.
In the Command Line, paste `pip install -r requirements.txt` and hit `ENTER`.

[Video](https://i.imgur.com/vpQiKhF.mp4)

### Linux

Debian: `sudo apt-get install python3`

* In this folder do: `pip install -r requirements.txt`
* To allow execution: `chmod +x ease_generator.pyw`

See [Tutorial Video (YouTube)](https://youtu.be/1c1yGZ14XYo)

## Usage

Double click the ease_generator.pyw file to run the program.

* Make the necessary settings for fps, duration (in seconds), start and end position and of course select the type of easing
* Click on "Generate and copy".
* Go in kdenlive
* Add a transform effect to a clip.
* In the transform effect, Click the hamburger menu button left to the timestamp.
* Select "Import Keyframes from Clipboard..."
* Change the time offset (if necessary)
* Disable "Limit keyframe number"
