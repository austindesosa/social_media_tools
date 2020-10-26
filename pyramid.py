# -*- coding: utf-8 -*-
"""pyramid.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1StluHCxOKTbBEyZqlPQH9S_mO3djyUD-

This file has to do with speech and audio. The next code cell includes some necessary pip installs and imports, as well as a function to extract a numpy array from an MP3 file:
"""
import os

os.system("pip install pydub")
os.system("sudo apt-get install python-pyaudio python3-pyaudio")
os.system("sudo apt-get install python3 python3-all-dev python3-pip build-essential swig git libpulse-dev")
import pyaudio

from pydub import AudioSegment
import numpy as np
from IPython.display import Audio
from scipy.io import wavfile
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers as lay, preprocessing as prep
import skimage.io as skio

from tensorflow.keras.preprocessing.text import Tokenizer
from sklearn.feature_extraction.text import CountVectorizer

os.system("pip install SpeechRecognition")
os.system("pip install -U textblob")
import speech_recognition as sr
from textblob import TextBlob

def mp3_data(src, dst='', ndx=0):
  '''<MP3 filename>, <WAV filename> empty by default, <Index> of column to take in case of 2D matrix
  REturns a tuple containing the framerate and an array of the sound data
  for a WAV file containing same sound as the MP3.
  Also creates such a WAV file as a by-product'''
  if not dst:
    dst+=src.split('.')[0]
    dst+='.wav'
  seg=AudioSegment.from_mp3(src)
  seg.export(dst, format='wav')
  (fr,sound)=wavfile.read(dst)
  if sound.ndim>1:
    sound=sound.T[ndx]
  return (fr, sound)

def unity(x):
  '''<Input>
  Returns the input
  Only purpose is to have it in function form'''
  return x



def downsample_1D(array, n = 5, func=np.mean):
  '''< 1D numpy array>, <elements per average> , <function> used to calculate numbers in return array
  Returns numpy array with 1/n as many elements, by grouping every <n> components and averaging them,
  putting the average in corresponding places in return array
  Meant to shorten an array from a WAV file while still preserving the sound
  NOTE: To do something Other than averaging to the samples, 
  you can use a different Python function as the <func> parameter'''
  reps=array.size//n
  ret = np.zeros(shape=(reps))
  i, bookmark = 0,0
  while i<reps:
    nextmark = min(bookmark+n, array.size)
    ret[i]=func(array[bookmark:nextmark])
    bookmark = nextmark
    i+=1
  return ret

def lowpitch(arr, n=10):
  '''Like downsample_1D, but 
  picks the Minimum values instead of the averages'''
  return downsample_1D(arr, n, np.min)


def hipitch(arr,n=10):
  '''Like lowpitch, but picks Maximum values instead of minimum'''
  return downsample_1D(arr,
                       n,
                       np.max)

def process_sound(fr, sound, n_samp=5, amp_shrink=0x8000, dtype = np.float32):
  '''<Framerate> in frames per second, <1D array> representing sound, 
  <Number of Samples> taken per average, <Amplitude shrinking factor>, <Data type>
  Processes the sound by converting to float data type, downsampling, and shrinking the amplitude
  Returns tuple containing (framerate, sound)
  WARNING: Mutates the parameters <fr> and <sound>'''
  sound = sound.astype(dtype)
  sound /= amp_shrink
  sound = downsample_1D(sound, n=n_samp)
  fr = int(fr/n_samp)
  return (fr, sound)

def transcribe(wf, rcr):
  '''<WAV file or filename>, <speech_recognition.Recognizer object>
  Returns string containing transcript of any English words spoken in the WAV file '''
  with sr.AudioFile(wf) as source:
    aud=rcr.record(source)
    s=rcr.recognize_google(aud)
  return s

"""Next we will test out the function:

The following code cell contains a class caled Mixtape, intended to make snd use sound files:
"""





class Mixtape:

  def __init__(self, array, fr):
    '''array : Numpy array representing the sound , datatype is 1-dimensional ndarray
    fr : Framerate, in frames per second, at which to play the sound 
    '''
    self.array = array
    self.fr = int(fr)
    self.rec=sr.Recognizer()
    

  @classmethod
  def from_mp3(cls, mp3):
    (fr, sound)=mp3_data(mp3)
    return Mixtape(sound, fr)

  @classmethod 
  def from_wav(cls, wav):
    (fr, sound)=wavfile.read(wav)
    return Mixtape(sound , fr)



  def to_array(self):
    return np.asarray(self.array)

  def to_audio(self):
    return Audio(self.array, rate=self.fr)

  def to_wav(self, fname='mixtape.wav', k_rate=1):
    wavfile.write(fname, int(k_rate*self.fr), self.array)
      

  def index_t(self, tsec):
    '''<float> representing time in seconds since the beginning of the audio
    Returns int for index in the array representing sound at time <sec>'''
    ndx=0+tsec
    ndx*=self.fr 
    return int(ndx)

  def t_section(self, t_start, t_stop):
    ndx_start, ndx_stop = self.index_t(t_start), self.index_t(t_stop)
    return self.array[ndx_start : ndx_stop]

  def from_section(self, t_start, t_stop):
    v=self.t_section(t_start, t_stop)
    return Mixtape(v, self.fr)

  def section_matrix(self, t_begin, t_end, t_delta=3.0):
    n_delta=int(t_delta * self.fr)
    height = int( (t_end-t_begin)//t_delta )
    start = int(t_begin * self.fr)
    stop = start+int(n_delta*height)
    v=self.array[start:stop]
    return v.reshape((height, n_delta))
    return v

  def full_transcript(self, 
                      namestub='son_',
                      delta=3.9):
    mat = self.section_matrix(0, self.array.size//self.fr, delta)
    rg, tapes = mat.shape[0],[]
    for i in range(rg):
      tapes.append(Mixtape(mat[i],self.fr))
    eng=''
    for i in  range(rg):
      x=namestub+str(i)+".wav"
      tapes[i].to_wav(x)
      try:
        eng += transcribe(x, self.rec)
      except:
        eng += "<OOV>"
      finally:
        eng += '\n'
    return eng

  def make_txt(self, name, namestub = "son_", delta = 3.5):
    with open(name, 'a') as f:
      x=self.full_transcript(namestub, delta)
      f.write(x)
      #return f

