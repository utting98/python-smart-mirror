"""
Python Smart Mirror Voice Control Launcher
Joshua Utting
27/10/2019

This code launches the voice control, a seperate launcher has been made such that if the voice control starts processing too slowly or
crashes after running for a long time it will attempt to re-launch itself so that the voice control does not stop operating for long
periods of time

"""

#These are imports use within Voice.py and are lsited here just incase
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

#launch function, this will attempt to continuously relaunch Voice.py if it errors or returns as it has been operating for too many
#iterations that could reach the request limit for the speech recognizer
def launch():
    try:
        while True:
            #this is not a good method of launching files I do not recommend you use this in projects unless you really have to
            exec(open('Voice.py').read()) 
    except:
        while True:
            exec(open('Voice.py').read())
#continuosly launch the launcher          
while True:
    launch()