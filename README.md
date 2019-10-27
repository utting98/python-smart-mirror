# python-smart-mirror

This code is the standard shell and relevant files of the smart mirror that I have written in python. The code visible here has had some sections omitted due to them containing person details relevant to me or API keys relevant to me. In order for the code to run for a user it will need modification to edit this. Sections that may want to be modified or have sections missing due to personal details have nearby commments inside triple quotes to stand out and show those areas need attention. The football score function has been temporarily omitted but will be replaced later, this is due to some minor display bugs that I have now attempted to fix but I can only test if Leicester City are playing.

On line 94 an API key is needed for getting the current weather conditions. This API is free and can be obtained from openweathermap.org, once this is in place this widget will function as expected.

Part of user2's section in the ttload() function is omitted because the method included sending details to log in to their work website, the method used to do it is described in the comments there incase someone wanted to make something similarly functioning. I have left a placeholder image in place of the timetable, normally the timetable would be replaced with an up to date one from their workplace's website but with the omitted section this will just show the same placeholder image when user2 is detected. Similarly user1's timetables in the Timetables folder have been replaced with placeholder images so that the functionality can be seen but without revealing info.

The following files need to be replaced with an alternative as they were omitted to protect personal details: a clear photo of the first user in facial recognition showing all facial features named user1.png in the same directory as the code, the same is also needed for user2.png, if you program to add any additional users (it is explained how to do this at the relevant point in the code) the you will also need a clear image of that user for the facial recognition.

In order for the mirror to run several things need to be installed. First ensure that on the device you have VLC media player installed, this is because streaming audio from youtube is done through VLC media player using a python library to control it. Secondly ensure you have Visual Studio installed with a C++ compiler, this is because setting up some of the libraries to install requires C++ compiling. Third ensure you have Chrome or Chromium web browser installed, this is because streaming music from youtube opens a chrome selenium window to automatically find the video, this could be potentailly worked around see documents online about using Selenium Web Browser with your desired browser and adjust the code accordingly (see Voice.py). Next add the directory where you keep the mirror software to your PATH variable. This can be done on windows by doing the following: search for "edit environment variables for your account" and open it. If you see a variable listed as "Path", single click on it and click edit. If you do not see a variable called "Path", click on "New" and name it "Path". If you are editing the existing "Path" variable you will see a list of directories from your computer, click on the "New" button and paste in to the text field the directory of the mirror python (ensurine chromedriver.exe is in the same place) then click ok and close the window. This is required as chromedriver.exe is searched for within the Path variable and if it not found you will get an error. Once these steps are all completed you can install all of the required libraries using pip, I use anaconda distribution of python so below is how I install them but you may need to follow different steps if you use another distribution:

Open Anaconda Prompt (A variation of command prompt for anaconda)

Type: cd [Paste the directory of the mirror code here] and press enter. This should set the directory of the prompt to where the mirror is.

Type: pip install -r requirements.txt and press enter. This will read the requirements text file and install each of the libraries one by one. If you followed all of the steps above there should hopefully be no errors, if there are errors let me know and I will try to resolve them then add them to the steps above. I particularly had trouble with cmake library so watch out for it.

If all libraries were installed succesfully you will get a message to the same tune that it was succesful. If a library was unsuccessful then there will likely be red text in your window, take a copy of that text so we can figure out how to resolve any install issues.

If all of the steps above are completed then you should now be able to run the mirror software. The way I do this is by opening two more anaconda prompts (or your alternative), set the directory as the location of the mirror code as you did for the installation and in one of the windows type: 

python Launch.py then press enter 

This will launch the voice control (you should do this one first as the mirror will not allow any window to go above it, unless you turned this off, until you alt+f4 out of it, also ensure you are clicked in to the mirror window when you do this). Next switch to the other anaconda prompt window and type:

python Mirror.py the press enter

This will begin loading the Mirror software, note that this will take a minute or two to process on launch but will update much faster than that after the initial loading period. At this point both the mirror and the voice control should be operational, from this point on you can close the software if you want to and you can go through and edit whatever you want and make the mirror suitable for your own personal use following the same kind of methods that I used. I am happy to permit the use of this software for your own personal use by making and customising your own mirror but not for commerical use or sale.

The current voice commands are as follows:

-mirror play [name of song or youtube video], this will stream audio of the first result from your youtube search term.

-mirror [date] [event], this will add and event to the event list which will be displayed in the bottom right of the mirror window.

-mirror calculate [simple calculation string], this will attempt to calculate what you have said and say the mathematical result back to you (note generally processable commands involve: plus, minus/subtract, divided by, times, to the power, square root but it can be a little temperamental if it mishears or you use another operator).

-mirror flip a coin, this will calculate a pseudo random probability which if above 0.5 the mirror will say you got tails and below 0.5 the mirror will say you got heads.

Thanks for your interest in this project.
