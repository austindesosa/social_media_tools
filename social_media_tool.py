# -*- coding: utf-8 -*-
"""social_media_tool.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1wA9N3NkQKQL38bsClPtcIUhXX42m4prH
"""



"""This file is meant to combine 3 modules I have previously written -- pyramid, somed, and test_by_color.

The file **pyramid.py** is for sound processing and speech-to-text. 

The file **somed.py** is to get information from popular social media platforms such as Instagram and GitHub.

The file **test_by_color.py** is to quickly train and test neural networks to distinguish between colors. This is a dummy task to test network architectures.

The file **aws_tool.py** is to interact with AWS resources

This file aims to combine these modules into one tool to collect visual and sound data from the Internet and use it to train and test neural networks.
"""

#Import built-in packages
import os
os.system('pip install -r requirements.txt')
import glob
import numpy as np
import skimage.io as skio
import json
import pandas as pd
import sqlite3 as sql

import tensorflow as tf
from tensorflow import keras
import torch

#Import other python modules in this directory
import somed
import pyramid as pyr
import test_by_color as tbc
import tf_cat
import aws_tool as aws

imread = np.vectorize(skio.imread)