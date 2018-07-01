#!/usr/bin/python2.7

import urllib2
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('AGG')
import matplotlib.pyplot as plt
import seaborn as sns
import cgitb
import cgi

cgitb.enable(display=0, logdir='./logs/')
print "Content-type: text/html\n"
print
print("[1,2,3,4,5,6,7,8]")
