# python-smart-mirror

This code is the standard shell and relevant files of the smart mirror that I have written in python. The code visible here has had some sections omitted due to them containing person details relevant to me or API keys relevant to me. In order for the code to run for a user it will need modification to edit this. Sections that may want to be modified or have sections missing due to personal details have nearby commments inside triple quotes to stand out and show those areas need attention.

On line 94 an API key is needed for getting the current weather conditions. This API is free and can be obtained from openweathermap.org, once this is in place this widget will function as expected.

Part of user2's section in the ttload() function is omitted because the method included sending details to log in to their work website, the method used to do it is described in the comments there incase someone wanted to make something similarly functioning. I have left a placeholder image in place of the timetable, normally the timetable would be replaced with an up to date one from their workplace's website but with the omitted section this will just show the same placeholder image when user2 is detected. Similarly user1's timetables in the Timetables folder have been replaced with placeholder images so that the functionality can be seen but without revealing info.

The following files need to be replaced with an alternative as they were omitted to protect personal details: a clear photo of the first user in facial recognition showing all facial features named user1.png in the same directory as the code, the same is also needed for user2.png, 
