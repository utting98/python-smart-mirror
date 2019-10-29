"""
Python Smart Mirror Display Software
Joshua Utting
24/10/2019

This code controls the display and updating for my version of a smart mirror. This is the public version and as such my APIs have
been removed and my personal information has as well so the code will not run as is. Anywhere that you need an API filling in will be
marked with this style of comment. Read the README file for info about what has changed from my functioning version so you know how 
to customise this code if you want to use it. The features in this code are as follows: time [top left], date [2nd from top left],
weather [center left], news [bottom left], face recognition switching display [top right], events list [bottom right]. For the voice
control a seperate instance of Launch.py needs to be ran, that code is unchanged so the voice recognition will work on running, see
those files for details. An API has been removed from the weather function which you can replace with a free API for current weather
from openweathermap.org, the login details have been removed from user2's facial recognition function but the code to see how it 
would have otherwise worked has been left in incase someone wants to run something similar. I have also omitted the livescore because
it had one or two display errors whihch I think I have fixed but not yet able to test until a game is played.

"""


from tkinter import *
import time
import geocoder
import requests
import json
import matplotlib.pyplot as plt
from PIL import Image,ImageTk
from io import BytesIO
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime
from datetime import datetime as dt
from bs4 import BeautifulSoup
from datetime import timedelta
import PIL.ImageOps
import face_recognition
import cv2
import numpy as np
from lxml import html
from selenium import webdriver

#function to run the clock, if the minute has changed update the label that contains the time to the new time
def tick(var,clock):
    global time1
    # get the current local time from the PC
    time2 = time.strftime('%H:%M')
    # if time string has changed, update it
    if time2 != time1:
        time1 = time2
        var.set(time2)
    # calls itself every 200 milliseconds
    # to update the time display as needed
    # could use >200 ms, but display gets jerky
    clock.after(200, lambda: tick(var,clock))

#get the suffix on the date passed
def suffix(d):
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')

#cut off the date suffix for comparing datetime objects and return datetime object in same format
def custom_strptime(format,t):
    try:
        t = t[0:2] + t[4:]
        date = datetime.strptime(t,'%d %B %Y')
    except:
        t = t[0] + ' ' + t[2:]
        date = datetime.strptime(t,'%d %B %Y')
    return date

#make a custom datetime object from the date string and suffix on date number
def custom_strftime(format, t):
    return t.strftime(format).replace('{S}', str(t.day) + suffix(t.day))

#function to check if the date has changed and if it has update the label displaying the date
def date(var,todayf):
    global datel
    
    date2 = custom_strftime('%A, {S} %B', dt.now()) #format the current datetime in the same way as the old date
    
    #if date has changed update todays date variable and update the label dusplaying date
    if date2 != todayf: 
        todayf = date2
        var.set(date2)
    datel.after(200, lambda: date(var,datel)) #reload after 200ms

#function to update the weather
def weatherupdate():
    global weatherframe,wreset,canvas
    
    wreset += 1
    if(wreset>1):
        canvasdestroy(canvas)
    else:
        pass
    
    """
    Below where it says weatherapi you must get a free api key from openweathermap.org for getting the current weather
    
    """
    weatherapi = 'API_STRING_HERE'
    
    base_url = "http://api.openweathermap.org/data/2.5/weather?" #Define base URL for all cases
    
    g = geocoder.ip('me') #Take IP from device and run it through geocoder to get location
    lat = str(g.latlng[0]) #Define latitude from geocoder data
    long = str(g.latlng[1]) #Define longitude from geocoder data
    complete_url=base_url+"lat="+lat+"&lon="+long+"&appid="+weatherapi #Define full URL to look up weather for this case via openweathermap
    response = requests.get(complete_url) #Get the response from the website
    x=response.json() #Define x as the json data response
    
    y=x["main"] #Define y as the main section of the json data
    current_temp = y["temp"] #Define current temperature from the main section
    current_pressure = y["pressure"] #Define current pressure from the main section
    current_humidity = y["humidity"] #Define current humidity from the main section
    z = x["weather"] #Define weather a z from the weather section of the json data
    weather_description = z[0]["description"] #Define a description of the weather from z
    weather_code = z[0]["icon"] #Define an image code to match description of weather from z
    
    #This is a small catch if the weather description is very long it would cut off the edges of the mirror
    #This will just take the final two workds of the weather description
    lengthcheck = weather_description.split(' ') 
    if(len(lengthcheck)>2):
        weather_description = str(lengthcheck[-2]+' '+lengthcheck[-1])
    else:
        pass
    
    weather_description = weather_description.title() #Capitalise first letter of each word in weather_description
            
    current_temp=float(current_temp-271.15) #Convert temperature to Celsius from Kelvin and add 2 degrees based on empirical running and comparing to other sites (value - 273.15 +2)
    
    weathericon = "http://openweathermap.org/img/w/"+weather_code+".png" #Find image by its code on openweathermap
    imageresponse = requests.get(weathericon) #Get the image response from the site
    image=Image.open(BytesIO(imageresponse.content)) #Open the image for use in the program
    
    f=Figure(figsize=(8,5),facecolor='black') #Define first figure with appropriate size
    f.patch.set_facecolor('xkcd:black')
    a=f.add_subplot(111) #Add subplot to figure
    a.imshow(image) #Plot the image on axes
    a.axis('off') #Switch off the plot axes for the image
    a.set_title((str(weather_description)+', '+str(int(current_temp))+'°C'),fontsize=40,color='white',weight='bold')
    a.set_facecolor('xkcd:black')
    
    canvas = FigureCanvasTkAgg(f, master=weatherframe) #Create canvas in GUI with figure on it
    
    canvas.get_tk_widget().grid(row=6,column=0,pady=75) #Pack canvas widget in GUI and allow to expand to fit graphs
    canvas.get_tk_widget().configure(background='black',highlightcolor='black', highlightbackground='black')
    canvas._tkcanvas.grid(row=6,column=0,pady=75) #Pack canvas in GUI and allow to expand to fit graphs

    weatherframe.after(900000, weatherupdate) #update every 15  minutes (timer is in milliseconds)

#remove the old canvas displaying weather
def canvasdestroy(canvas):
    canvas.get_tk_widget().destroy() #Destroy first canvas widget
    return

#function to get the news headlines
def getnews(var,newslabel):
    result = requests.get("http://www.bbc.com/news") #get the bbc news page
    soup = BeautifulSoup(result.content, "lxml") #parse the html tags on the page content
    headlines = soup.find_all("h3") #all headlines have a h3 tag so search for all instances of this tag
    lines=[] #define empty headlines list
    #for the headline tags found append the list with the text inside the tags
    for headline in headlines:
        lines.append(headline.text)
    finallines = list(dict.fromkeys(lines)) #remove any duplicate headlines
    #update the label of the headlines with the first 5 headlines found
    var.set('\n\nBBC News:\n[1] - %s\n[2] - %s\n[3] - %s\n[4] - %s\n[5] - %s\n'%(finallines[0],finallines[1],finallines[2],finallines[3],finallines[4]))
    
    newslabel.after(900000,lambda: getnews(var,newslabel)) #update every 15 minutes
    
#check if the list of stored events has changed and call function to cycle through events if too many to list
def checkevents(var,eventlabel):
    global week, day, newcall
    changed=False
    #read in the data from eventslist text file and split at comma to get date and event details for each stored event
    readfile = open('eventslist.txt','r')
    events = []
    week = []
    day = []
    for line in readfile:
        splitup = line.split(',')
        events.append(splitup)
    readfile.close()
    #check if the current datetime has exceeded any datetime listed in the events, if the date of an event is past then mark
    #the i-th element of delarray as 1 to flag a positive to kill the event
    delarray = [0]*len(events)
    for i in range(0,len(events)):
        if(((custom_strptime('{S} %B %Y', events[i][0])).date()-dt.now().date()).days<0):
            delarray[i]=1
            changed = True
        else:
            pass
    #check through delarray and if one is flagged for deletion remove it from the events list
    for i in reversed(range(len(events))):
        if(delarray[i]==1):
            events.pop(i)
        else:
            pass
    #if there has been an event deleted then overwrite the events list text file to avoid wasting data storage on expired events
    if(changed==True):
        file = open('eventslist.txt','w')
        for i in range(0,len(events)):
            file.write(events[i][0]+','+events[i][1])
        file.close()
        changed=False
    else:
        pass
    #get current date and format it in a consistent style, then check if the event is dated the same as the current date, if so
    #then append the day list for events today, or if the event date is within 7 days of the current date append the week list for
    #events upcoming this week
    cdate = custom_strftime('{S} %B %Y', dt.now())
    for i in range(0,len(events)):
        for j in range(1,7):
            
            if(custom_strftime('{S} %B %Y', dt.now()+timedelta(j))==events[i][0]):
                week.append(events[i])
            else:
                pass
        if(cdate==events[i][0]):
            day.append(events[i][1])
        else:
            pass
    #if no events today or this week run cycleweek witht this info and set the event label to say no upcoming events
    if(day==[] and week==[]):
        newcall=1
        cycleweek(var)
        var.set('No Upcoming Events')
    
    #if there are events this week but not today construct a string of all the events in the format [date]:[newline][event] etc
    elif(day==[] and week!=[]):
    
        weekstring = ''
        for i in range(0,len(week)):
            weekstring = str(weekstring) + str(week[i][0]) + ':\n' + str(week[i][1]) + '\n'
        #if there is more than 2 events this week then call the function to cycle through 1 by 1 but if not display the event string
        if(len(week)>2):
            newcall=1
            cycleweek(var)
        else:    
            var.set('Events This Week:\n%s' % weekstring)
    #if there are events today but not this week do the same thing as the reverse situation above but with the day events
    elif(day!=[] and week==[]):
   
        daystring = ''
        for i in range(0,len(day)):
            daystring = str(daystring) + str(day[i]) + '\n'
        
        if(len(day)>2):
            newcall=1
            cycleweek(var)
        else:            
            var.set('Events Today:\n%s' % daystring)    
    #if there are events today and this week construct a daystring and weekstring as above
    elif(day!=[] and week!=[]):
        
        daystring = ''
        for i in range(0,len(day)):
            daystring = str(daystring) + str(day[i]) + '\n'
        weekstring = ''
        for i in range(0,len(week)):
            weekstring = str(weekstring) + str(week[i][0]) + ':\n' + str(week[i][1]) + '\n'
        #if either the day or week has more than 2 events then run the cyclling function through each of the events, but if not
        #display the days events followed by the weeks events
        if(len(week)>2 or len(day)>2):
            newcall=1
            cycleweek(var)
        else:    
            var.set('Events Today:\n%s\nEvents This Week:\n%s' % (daystring,weekstring))
        
    eventlabel.after(1000, lambda: checkevents(var,eventlabel)) #loop through every second

#continuation of the checkevents function for cycling events if there are too many
def cycleweek(var):
    global week, day, cevent, devent, newcall, weekold, dayold
    #if the day and week arrays have changed update the "old" version to the current version to see if something changes again
    if(newcall==1):
        weekold = week
        dayold = day
    else:
        pass
    #if both are empty check to see if it has changed from the old version, if yes return to see which event classification is now
    #correct, if not then just set the label as no upcoming events and return to check the list again
    if(day==[] and week==[]):
        if(weekold!=week or dayold!=day):
            newcall=1 
            return
        var.set('No Upcoming Events')
        return
    #if day is empty and week is not empty cycle through the events list displaying the week evemts one by one and waiting five
    #seconds between each to allow you to read them
    elif(day==[] and week!=[]):
        for i in range(0,len(week)):
            cevent = str(week[i][0]) + ':\n' + str(week[i][1]) + '\n'
            if(weekold!=week or dayold!=day):
                newcall=1
                return
            else:
                pass
            var.set('Events This Week:\n%s' % cevent)
            root.update()
            time.sleep(5)
    #works as the one above but if day is not empty and week is empty
    elif(day!=[] and week==[]):
        for i in range(0,len(day)):
            devent = str(day[i]) + '\n'
            if(weekold!=week or dayold!=day):
                newcall=1
                return
            else:
                pass
            var.set('Events Today:\n%s' % devent)
            root.update()
            time.sleep(5)
    #if day and week events aren't empty loop through both simultaneously the same as was done with the individual lists, if the 
    #lists aren't the same length then the shorter one will pause on the final event in the list until the longer one is done 
    elif(day!=[] and week!=[]):
        if(len(week)>len(day)):
            lmax = len(week)
        else:
            lmax = len(day)
        for i in range(0,lmax):
            try:
                cevent = str(week[i][0]) + ':\n' + str(week[i][1]) + '\n'
            except:
                cevent = cevent
            try:
                devent = str(day[i]) + '\n'
            except:
                devent=devent
            if(weekold!=week or dayold!=day):
                newcall=1
                return
            else:
                pass
            var.set('Events Today:\n%s\nEvents This Week:\n%s' % (devent,cevent))
            root.update()
            time.sleep(5)
    else:
        pass
    newcall+=1
    return #return back to check if the events changed

"""
This function uses the results from the facial recognition, the facial recognition will need two images in the folder that this code
is in, one image called user1.png and one image called user2.png, they need to be clear photos of ths users with all facial details
visible, if there are issues print out from the main [user]_face_encoding and if its an array of non-zero numbers the image was
successful, if not then you need to use a different image. It will be shown that you can easily add more users to the facial
recognition by repeating what you do for the existing users below. If you add additionbal users then just add an elif(user=='user3')
blow and program in what you want it to do for that user
"""
#check user and load the timetable of the appropriate user
def ttload():
    global loadtable, face_names, oldface, firstloop, changed, user, firstrun, titlelabel
    #run the facial recognition function to check if a user is infront of the camera
    facerecog()
    #if it is the first run the code will set a backup to user1 if no user is detected
    if(firstrun==True):
        oldface='user1'
    else:
        pass
    #this is a massive run to check which user to use
    try:
        #face names is an array of faces detected from facial recognition, if it matches one of the users code will set current user
        #to the first face found
        if(face_names[0]=='user1' or face_names[0]=='user2'):
            user = face_names[0]
            #if the user has changed flag it as changed, means something new needs to be displayed
            if(user!=oldface):
                changed=1
            #if user has not changed do not flag it as changed, this is to stop elements flashing as they are re-displayed when
            #nothing has changed
            else:
                changed=0
            oldface = face_names[0] #set the last user to the current user to make change detection possible
        #if a known user is not detected display the information of the last user, this can be adapted to display nothing if you
        #only want elements to display when the permitted user is present, also flag changed as zero as user hasn't changed
        else:
            user = oldface
            changed=0
    except:
        #if user detection has failed for any reason try to default back to the last user and mark as unchanged
        try:
            user=oldface
            changed=0
        #if backup fails just refer back to user one, again it is possible to adapt this to only display the user's setup if they
        #are present and this marks as unchaged
        except:
            user='user1'
            changed=0
    #if it's the first run mark as changed to force displaying the elements for first loop
    if(firstrun==True):
        changed=1
    else:
        pass    
    #no longer firstrun
    firstrun=False
    #open a file to check if user1's display has been updated today (for swithcing timetables overnight etc.)
    file = open('Cday2.txt','r') #(Current day 2)
    for line in file:
        updateday = line
    file.close()
    daynow = dt.now().strftime('%d')
    #if day has changed write the new day (as a number) to the check file
    if(updateday!=daynow):
        changed=1
        file = open('Cday2.txt','w')
        file.write(dt.now().strftime('%d'))
        file.close()
    else:
        pass
    #if user 1 profile is active
    if(user=='user1'):
        #and if the user has changed so it knows the display needs changing
        if(changed==1):
            """
            This bit of code is specific to loading my uni schedule, as it comes under personal details for hence the timetable images 
            have been removed but this works by checking the word name of the current day and then finding the appropriate timetable
            from the timetables folder to display
            """
            day = dt.now().strftime('%A')
            days = ['Monday','Tuesday','Wednesday','Thursday','Friday']
            ttims = ['./Timetables/TimetableMon.png','./Timetables/TimetableTues.png','./Timetables/TimetableWeds.png','./Timetables/TimetableThurs.png','./Timetables/TimetableFri.png']
            
            #I recommend you keep this, it removes the title which can be set below in titlelabel to highlight what will be displayed
            #underneath it 
            check = ttframe.grid_slaves(row=0,column=0)
            if(check!=[]):
                titlelabel.grid_forget()
            else:
                pass
            #set and display a title for this frame
            titlelabel = Label(ttframe,text='Uni Schedule:',font=('Helvetica', 20, 'bold'), fg = 'white',bg='black')
            titlelabel.grid(row=0,column=0,sticky='nsew')
            #try and find the index of the current day from the days list, if succeeds it will return a number else it will return Fail
            try:
                val = days.index(day)
            except:
                val = 'Fail'
            #if it has found an integer meaning uni occurs on that day it will load the timetable image with the same index as the
            #appropriate day, colours are inverted to make the timetable black (can be removed i you are displaying something black)
            if(isinstance(val,int)):
                image = Image.open(ttims[val])
                inverted_image = PIL.ImageOps.invert(image)
                photo = ImageTk.PhotoImage(inverted_image)
                #also recommend leaving in, checks if the space for the image is filled, if it is removes the old image
                check = ttframe.grid_slaves(row=1,column=0)
                if(check!=[]):
                    loadtable.grid_forget()
                else:
                    pass
                #display the image in the appropriate part of the window
                loadtable = Label(ttframe,image=photo)
                loadtable.image=photo
                loadtable.grid(row=1,column=0)
            #if it returned failed then remove the image and display text saying there is no uni today
            else:
                check = ttframe.grid_slaves(row=1,column=0)
                if(check!=[]):
                    loadtable.grid_forget()
                else:
                    pass
                loadtable = Label(ttframe,text='No Uni Today!',font=('Helvetica', 20, 'bold'), fg = 'white',bg='black')
                loadtable.grid(row=1,column=0)
            #reset changed to 0
            changed=0
        #if not changed don't do anything
        else:
            pass
    #if user is user2
    elif(user=='user2'):
        #and user has changed
        if(changed==1):
            #remove anything displayed in the appropriate frame to avoid overlap
            check = ttframe.grid_slaves(row=1,column=0)
            if(check!=[]):
                loadtable.grid_forget()
            else:
                pass
            
            check = ttframe.grid_slaves(row=0,column=0)
            if(check!=[]):
                titlelabel.grid_forget()
            else:
                pass
            #set a new title of work schedule (user two comes up with what shifts they are on at work)
            titlelabel = Label(ttframe,text='Work Schedule:',font=('Helvetica', 20, 'bold'), fg = 'white',bg='black')
            titlelabel.grid(row=0,column=0,sticky='nsew')
            
            #check if user2's schedule has been updated today
            file = open('Cday.txt','r')
            for line in file:
                updateday = line
            file.close()
            daynow = dt.now().strftime('%d')
            #if user2's schedule has not been updated today run this code to find a new timetable
            if(updateday!=daynow):
                #instruct user that a new timetable is being found in the background and will continue processing whether they are
                #present or not
                loadtable = Label(ttframe,text='Loading New Timetable\nThis Will Take A Minute\nYou Can Go Do Something Else While This Processes',font=('Helvetica', 20, 'bold'), fg = 'white',bg='black')
                loadtable.grid(row=1,column=0)
                #update window to show new dispay
                root.update()
                #this is how i adjusted the widths to make everything fit in the screen properly, each works in pixel counts
                #basically adjusts the size of the space between the left and right sections of display, this can be edited to just
                #a standard value if you have the same size stuff each time so you know it won't spill off the screen
                lwidth = int(newsframe.winfo_width())
                rwidth = int(ttframe.winfo_width())
                rwidth2 = int(eventframe.winfo_width())
                crwidth = max(rwidth,rwidth2)
                totalw = int(root.winfo_screenwidth())
                finalw = totalw-(crwidth+lwidth)-100
                root.grid_columnconfigure(1, minsize=finalw)
                #update the window ti change the display
                root.update()
                
                """
                A section has been omitted here due to too much personal information, basically a selenium chrome window was opened
                in the background where the user can't see, this window loaded up user2's work website, logged in through both login
                windows required using driver.send_keys() then automated processes would take you through to the page where the
                timetable was kept. When the timetable was found selenium would screenshot the driver window and save the file as
                CTimetable.png, this would be the days updated timetable. Then the chrome window would be closed. Selenium was used
                as requests couldn't send enough header info to allow login through the code. You can see a selenium window being
                opened in the Voice.py code if you are trying to make a build with one then if you need to login look at
                driver.find_element_by_id and driver.send_keys in the documentation.
        
                """
                time.sleep(10) #this sleep is in to  simulate the time it would be processing a new timetable
                #update the day stored in the text file to say the timetable has been updated on said day for the next comparison
                file = open('Cday.txt','w')
                file.write(str(dt.now().strftime('%d')))
                file.close()
            
            #if timetable is already up to date then skip the process of getting new one to keep running fast
            else:
                pass
            
            #new timetable is opened and the sizes are taken
            image = Image.open('CTimetable.png').convert("RGBA")
            w, h = image.size
            
            #image is cropped because the fetched image had extra unnecessary white spoace around it, cropping can be removed if your
            #image to display is fine
            upper = 3*h/8
            
            img2 = image.crop([0,upper,(w-(w/5)),h])
            photo = ImageTk.PhotoImage(img2)
            
            #empty the content where the loading message is 
            check = ttframe.grid_slaves(row=1,column=0)
            if(check!=[]):
                loadtable.grid_forget()
            else:
                pass
            
            #display the timetable in the appropriate section
            loadtable = Label(ttframe,image=photo)
            loadtable.image=photo
            loadtable.grid(row=1,column=0)
            
            #automatically configure the widths again to fix any cut off display
            lwidth = int(newsframe.winfo_width())
            rwidth = int(ttframe.winfo_width())
            rwidth2 = int(eventframe.winfo_width())
            crwidth = max(rwidth,rwidth2)
            totalw = int(root.winfo_screenwidth())
            finalw = totalw-(crwidth+lwidth)-100
            root.grid_columnconfigure(1, minsize=finalw)
            #update the window
            root.update()
        
        #if user has not changed don't do anything
        else:
            pass
    #try and update the display, display wants different formatting depending on which user is active based on my displayed images    
    try:
        #if user1 then set these size conditions
        if(user=='user1'):
            root.grid_columnconfigure(2, minsize=450)
            crwidth=450
            lwidth = int(newsframe.winfo_width())
            totalw = int(root.winfo_screenwidth())
            finalw = totalw-(crwidth+lwidth)-100
            root.grid_columnconfigure(1, minsize=finalw)
        #if user2 active set the standard sizing conditions
        else:
            rwidth = int(ttframe.winfo_width())
            rwidth2 = int(eventframe.winfo_width())
            crwidth = max(rwidth,rwidth2)
            lwidth = int(newsframe.winfo_width())
            totalw = int(root.winfo_screenwidth())
            finalw = totalw-(crwidth+lwidth)-100
            root.grid_columnconfigure(1, minsize=finalw)
        #update the window
        root.update()
    except:
        pass

    root.after(200, ttload) #loop this function every 200ms

#function to recognise a face in the webcam
def facerecog():
    global known_face_encodings, known_face_names, face_locations, face_encodings, face_names, process_this_frame, face_names
    #this code is slightly adapted from the face_recognition library
    # Grab a single frame of video
    ret, frame = video_capture.read()

    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]

    # Only process every other frame of video to save time, I have switched to process every frame because I don't have this
    #constantly running, only when it's called in ttload function
    if process_this_frame:
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            # Or instead, use the known face with the smallest distance to the new face i.e. if facial features are within a
            #tolerance of where the picture specifies the library decides that is a match
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
            #element 0 of this array will be set as the user as long as it is not unknown as defined in ttload
            face_names.append(name) 
    
    #if you want to reduce frame processing rate from webcame uncomment line 627 and comment out line 628
    #process_this_frame = not process_this_frame
    process_this_frame=True
    return #return to the ttload function where this was called from

#entry point when running the code
if __name__=='__main__':
    #configure some attributes and set some variables for starting functions
    root = Tk() #window definition
    root.title('Smart Mirror') #set title for window
    root.wm_attributes('-fullscreen','true') #make window borderless fullscreen
    #set window to be above all other programs, not when trying to configure things this can get in the way so hash this line out
    #while running tests that your mirror is functioning as intended
    root.attributes("-topmost", True) 
    root.configure(background='black') #make background black for best transmission to reflection
    firstloop=True
    firstrun=True
    
    #This section of code setting up facial recognition is from the face_recognition documentation
    # Get a reference to webcam #0 (the default one)
    video_capture = cv2.VideoCapture(0)
    
    """
    More users can easily be added here by copying the method for user1 and user2 just add a photo to the directory called user3.png
    etc then copy the image and face encoding references for the new users. Next add the face encoding to the known_face_encodings
    list (in order), then add the known_face_names (what you want that user to be called, this is what you set the user name as in 
    the ttload function, also make sure it is in the same order as the known_face_encodings list).
    """
    
    # Load a sample picture and learn how to recognize it.
    user1_image = face_recognition.load_image_file("user1.png")
    user1_face_encoding = face_recognition.face_encodings(user1_image)[0]
    
    # Load a second sample picture and learn how to recognize it.
    user2_image = face_recognition.load_image_file("user2.png")
    user2_face_encoding = face_recognition.face_encodings(user2_image)[0]
    
    # Create arrays of known face encodings and their names
    known_face_encodings = [
        user1_face_encoding,
        user2_face_encoding
    ]
    known_face_names = [
        "user1",
        "user2"
    ]
    # Initialize some variables
    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True
    
    #place a frame for the time in the first row and column
    timeframe = Frame(root).grid(row=0,column=0)
    ctime = StringVar() #variable for the time
    #set clock label to use the variable ctime and define font and colours to match the root
    clock = Label(timeframe,textvariable=ctime,font=('Helvetica', 40, 'bold'), fg = 'white',bg='black')
    #display the clock label in row 0 and column 0 of the time frame
    clock.grid(row=0,column=0)
    time1 = time.strftime('%H:%M') #set current time on loadup
    ctime.set(time1) #set clock label to be current time
    #call the time function to keep updating the clock variable ctime and hence the label for the clock that is tied to it
    tick(ctime,clock) 
    
    #functions the same as the clock one, set current date as the date label in the clock frame next row then call the date function
    #to keep updating the date if it changes
    cdate = StringVar()
    todayf = custom_strftime('%A, {S} %B', dt.now())
    cdate.set(todayf)
    datel = Label(timeframe,textvariable=cdate,font=('Helvetica', 20, 'bold'), fg = 'white',bg='black')
    datel.grid(row=1,column=0)
    date(cdate,todayf)
    
    #make frame for weather widget
    weatherframe = Frame(root,bg='black')
    #grid the weather frame in the third row of root
    weatherframe.grid(row=2,column=0)
    wreset = 0 #initialise variable
    weatherupdate() #call function to keep updating the weather
    
    #defines frame and label for news widget, calls the function to load news headlines and updates the label variable with the title
    #and 5 headlines
    newsframe = Frame(root)
    newsframe.grid(row=3,column=0)
    newsvar = StringVar()
    newslabel = Label(newsframe,textvariable=newsvar,font=('Helvetica', 20, 'bold'), fg = 'white',bg='black')
    newslabel.grid(row=0,column=0)
    getnews(newsvar,newslabel)
    
    #defines frame for timetable widget on the right hand side spanning three rows because it displays a long image, calls function
    #to run facial recognition and display timetables
    ttframe = Frame(root)
    ttframe.grid(row=0,column=2,rowspan=3)
    ttload()
    
    #defines a blank framein the centre of the mirror to focus where reflection will be with info around, spans two rows
    blank = Frame(root,bg='black')
    blank.grid(row=2,column=1,rowspan=2)
    
    #update window
    root.update()
    
    #functions same as clock widget, calls checkevents function with the label variable being updated with current events in the
    #function call
    eventframe = Frame(root)
    eventframe.grid(row=3,column=2)
    eventvar = StringVar()
    eventlabel = Label(eventframe,textvariable=eventvar,font=('Helvetica', 20, 'bold'), fg = 'white',bg='black')
    eventlabel.grid(row=0,column=0)
    checkevents(eventvar,eventlabel)
    
    """
    If you want more widgets in your mirror just grid a new frame in a bit of space and call a function to update the display in it
    like the examples you can already see
    """
    #try and do the user based window sizes update as before
    try: 
        if(user=='user1'):
            root.grid_columnconfigure(2, minsize=450)
            crwidth=450
            lwidth = int(newsframe.winfo_width())
            totalw = int(root.winfo_screenwidth())
            finalw = totalw-(crwidth+lwidth)-100
            root.grid_columnconfigure(1, minsize=finalw)
        else:
            rwidth = int(ttframe.winfo_width())
            rwidth2 = int(eventframe.winfo_width())
            crwidth = max(rwidth,rwidth2)
            lwidth = int(newsframe.winfo_width())
            totalw = int(root.winfo_screenwidth())
            finalw = totalw-(crwidth+lwidth)-100
            root.grid_columnconfigure(1, minsize=finalw)
    #if user based fails like it will on the first iteration where user is not yet defined do the standard version of the update
    except:
        rwidth = int(ttframe.winfo_width())
        rwidth2 = int(eventframe.winfo_width())
        crwidth = max(rwidth,rwidth2)
        lwidth = int(newsframe.winfo_width())
        totalw = int(root.winfo_screenwidth())
        finalw = totalw-(crwidth+lwidth)-100
        root.grid_columnconfigure(1, minsize=finalw)
    
    #update the window
    root.update()
    #define mainloop to display the window
    root.mainloop()













