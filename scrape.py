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



def download(url, user_agent='wswp', num_retries=2):
    headers = {'User-agent': user_agent}
    request = urllib2.Request(url, headers=headers)
    try:
        html = urllib2.urlopen(request).read()
    except urllib2.URLError as e:
        print ('Download error:', e.reason)
        html = None
        if num_retries > 0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                # retry 5XX HTTP errors
                return download(url, user_agent, num_retries - 1)
    return html






def main():
    pass
    #giftplot('admlr')
    #form = cgi.FieldStorage()
    #if(form.has_key("param1")):
    #    user = form["param1"].value
    #    gameplot(user)



#cgitb.enable(display=0, logdir='./logs/')
main()
