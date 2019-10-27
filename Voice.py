"""
Python Smart Mirror Voice Control
Joshua Utting
27/10/2019

This code runs the operation of voice control within the smart mirror software. This works by recording your microphone with a
timeout period of 5 seconds then attempting to process the audio and check for command keywords within the transcription. The code
will check how long each conversion from speech to text took and if it was more than 15 seconds it returns back to the launcher
and relaunches this code to speed up operation again as it lags if use continuously. The same process occurs if it has ran 50 times
consecutively as preventative fixing.

"""
#import relevant libraries
import time
import speech_recognition as sr
import pyttsx3
import urllib.request
import pafy
import vlc
import pygame
import numpy as np
from selenium import webdriver
from bs4 import BeautifulSoup
import pyaudio

#function to recognise command, this will record and analyse the audio then run the appropriate command for what was said
def reccommand():
    global iterator #count how many loops
    try:
        r = sr.Recognizer() #define the speech recognition instance
        mic = sr.Microphone() #define the speech recognition microphone
        print(mic)
        engine = pyttsx3.init() #define the text to speech engine
    except:
        iterator=50 #if these fail reload te script
        return
    print('moved to command')
    months = ['January','February','March','April','May','June','July','August','September','October','November','December']
    with mic as source: #use mic as source to record audio from
        r.adjust_for_ambient_noise(source,duration=0.5) #adjust mic detection levels for 0.5s to reduce noise
        try:
            audio = r.listen(source,timeout=5) #record from microphone for 5 seconds
            iterator+=1 #increase the iterator, if you see the same number printing in the logs the audio record failed
            start = time.time() #take note of time
            recognised = r.recognize_google(audio) #use recognizer to make word string from audio file
            end = time.time() #take note of time finished
            tdiff = end-start #find time taken to analyse audio
            if(tdiff>15): #if it took more then 15 seconds to process then we want to exit and rerun the script to speed it up again
                iterator=50
                return
            else: #if took less than this it's ok
                pass
            command = str(recognised).split(' ') #split the recognised string by space
            print(command)
            
        except:
            pass

    try:#we will try to find a match in the issued command for known commands       
        if(('mirror' in command) and ('play' in command)): #if you said mirror play
            #make a beep noise to tell user it found a command word
            pygame.mixer.init()
            pygame.mixer.music.load("beep.wav")
            pygame.mixer.music.play()
            #find the position of the word play in the command
            pos = command.index('play')
            #join the words after play to make the search terms
            songlist = command[(pos+1):]
            songstring = ' '.join(songlist)
            query = urllib.parse.quote(songstring)
            url = "https://www.youtube.com/results?search_query=" + query #url for searching your request on youtube
            try: #try and open a chrome window to the url we just defined for searching
                driver = webdriver.Chrome() 
                driver.get(url)
                time.sleep(5) #wait for window to load page
            except:
                driver.close() #if it failed to load the page close the window, you will have to reissue the command
            links = []
            links.append(driver.find_element_by_id('video-title')) #find all the video links
            href = links[0].get_attribute('href') #get the url of each video link
            video = pafy.new(href) #direct to the first video in the results
            best = video.getbestaudio() #choose the source of said video with the best audio quality
            try:
                playurl = best.url #get the url of best audio
                player = vlc.MediaPlayer(playurl) #load audio link to vlc media player                                                                                                     
                player.play() #play the audio
                time.sleep(2) #wait to seconds to allow playing to commence
                driveropen=True #to remember that the chrome window is still open
                while(player.get_state()==vlc.State.Playing): #wait for the duration of the song before more commands are issued
                    if(driveropen==True): #if driver is still open
                        driver.close() #close the driver
                        driveropen=False #mark driver as closed
                    else:
                        pass
            except:
                driver.close() #if loading media failed close the driver
        
        elif(('mirror' in command) and any(month in command for month in months)): #check if you said mirror and a month 
            #make a beep noise to say command was recognised
            pygame.mixer.init()
            pygame.mixer.music.load("beep.wav")
            pygame.mixer.music.play()
            pos = command.index('mirror') #find the position of mirror as date will be after
            date = ' '.join(command[pos+1:pos+4]) #date string is words 1 to 3 after mirror
            event = ' '.join(command[pos+4:]) #event string is words 4 onward
            string = date+','+event+'\n' #comma separate the date and event
            writefile = open('eventslist.txt','a') #open eventslist to append to it
            writefile.write(string) #write the event to the file
            writefile.close() #close the file
        
        elif(('mirror' in command) and ('calculate' in command)): #check if you said mirror and calculate
            #make a beep noise to say command was recognised
            pygame.mixer.init()
            pygame.mixer.music.load("beep.wav")
            pygame.mixer.music.play()
            time.sleep(1) #make sure beep finished before say calculation string
            pos = command.index('calculate') #find where calculate was
            calcstring = command[(pos+1):] #calcstring is everything after calculate
            string = ' '.join(calcstring) #make one continuous string
            #series of replacements to allow evaluation of the calculation string
            try:    
                string = string.replace('x','*')
            except:
                pass
            try:
                string1 = string.replace('square root','np.sqrt(')
                if(string1!=string):
                    string = string1+')'
                else:
                    string = string
            except:
                pass
            try:
                string = string.replace('^','**')
            except:
                pass
            try:
                string = string.repalce('squared','**')
            except:
                pass                
            try:
                string = string.repalce('to the power','**')
            except:
                pass                
            try:
                string = string.replace(' ','')
            except:
                pass
            #use eval function to work out the maths string as a float
            evaluated = eval(string) #eval is a bad method and risky, only use in your projects if you have no other choice
            engine.say(evaluated) #load text to speak engine with the result
            engine.runAndWait() #say the loaded text
        
        elif('mirror' and 'coin' in command): #check if said flip a coin
            val = np.random.uniform(0,1) #choose random number between 0 and 1
            if(val<0.5): #if 0-0.4999... say heads 
                engine.say('Ok, you got heads')
                engine.runAndWait()
            else: #if 0.5-1... say tails
                engine.say('Ok, you got tails')
                engine.runAndWait()
    except: #if something failed don't do anything
        pass
  
    return #return to call
    
if __name__=='__main__': #entry point
    iterator = 0 #reset iterator
    while(iterator<50): #loop until 50 attempts
        reccommand() #call recognise command function again
        print(iterator) #to check if frozen
    
    
    
    
    
    
    
    
    
    