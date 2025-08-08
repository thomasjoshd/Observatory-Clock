# Observatory-Clock
A 24 hour analog/digital observatory clock.  It featuress local sidereal time, Greenwich sidereal time, UT, sunrise, sunset, percnet moon illumination and both Julian Date and MJD.  The analog display also shows the current right ascension of solar system objects.

The display name, fontsize, window size, and observatory location are all customizable.  Once you change and set the new observatory location it will create a settings.par file it will read each time it launches to remember your settings.  NOTE it must have correct latitude and longitude for it to correctly calculate the sunrise/sunset times. It should work on Linux/Mac/Windows (it has for me!)

# Installation
Python 3 is required.  And tnen you need to install the required packages:

$ pip install -r requirements.txt

# Launching the clock

It can be launched on Linux/Mac/Windows from a python/anaconda command line.

$ python Observatory-Clock.py

In Linux/Mac
It can also be launched by using the included customizable shell (bash/sh) script.  Which you could make exacutable if you wish.

$ bash Observatory-Clock.sh

On Windows I've included a .bat file, but you may need to modify the anaconda installation path, and the path to where you want to store Observatory-Clock.py.  Once you do that, you can double click the file to launch the clock.

# Detailed Description of reading the clock
The 24 hour display has black numbers on the outside for local time.  There is a screenshot of the Main Window included with the files, along with a screenshot of the settings window.

The blue numbers on the inner ring change on their own so that the meridian (indicated by the hour hand) is pointing to both the current right ascension of the meridian (local sidereal time) and the local civil time.

The purple and blue hour hands always move together and is color coordinated with the digital displays at the bottom.

The red hour hand indicates the UT time on the black ring of numbers, and corresponds to the red UT digital display.

The thin gray lines perpendicular to the purple/blue hour hands indicates 6 hours of hour angle, approximately the horizon at the celestial equator.

The planets are indicated by their astronomical symbols, they are approximately color coded red for Mars, Jupiter and Saturn are the same color as "giant" planets and Neptune and Uranus are blue for "ice giants". Their location is their right ascension, so it can be read from the blue set of numbers of the dial.  Their distances from the center (earth) follow a geocentric-type approach, the distances are not scaled and are set a fixed values that looked
nice. Venus and Mercury are black when inferior to the sun, and red when superior to the sun.

The sunset/sunrise times are color coordinated with marks on the dial and the nighttime hours are shaded.

The moon phase can be inferred from the relative position of the Sun, Earth, and Moon.  The Earth is at the center of the dial.  Since this is a clock, the moon moves clockwise in right ascension. To aid in interpreting phase 1st and 3rd quarters are marked, new moon is of course when the moon is between the sun and earth.
