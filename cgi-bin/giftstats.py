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


def giftplot(user='ak73'):
    html = requests.get('https://tengaged.com/gifts/' + user).text
    num_gifts = re.findall('<span class="remark">(.*?)</span>', html)[0]
    num_pages = np.ceil(float(num_gifts) / 15)
    soup = BeautifulSoup(html, 'html.parser')
    gifts_db = pd.DataFrame(columns=['user', 'num_gifts'])

    for i in range(1, int(num_pages) + 1):
        html = requests.post('https://tengaged.com/gifts/' + user, {'action': 'loadGifts', 'p': i})
        soup = BeautifulSoup(html.text, 'html.parser')
        gifts = soup.findAll(attrs={'class': 'gifts imgMsgList big'})[0]
        gifters = gifts.findAll(attrs={'class': 'message'})
        for gifter in gifters:
            try:
                cuser = gifter.find_all('a')[0].text.__str__()
            except:
                continue
            if cuser in list(gifts_db.user):
                index = gifts_db.user[(gifts_db.user == cuser)].index[0]
                current_count = gifts_db.iloc[index].num_gifts
                gifts_db.set_value(index, 'num_gifts', current_count + 1)
            else:
                gifts_db = gifts_db.append({'user': cuser, 'num_gifts': 1}, ignore_index=True)

    gifts_db.num_gifts = gifts_db.num_gifts.astype(int)
    try:
        top10 = (gifts_db.nlargest(10, 'num_gifts'))
    except:
        top10 = gifts_db

    a = sns.barplot(top10.user, top10.num_gifts).set_title(user)
    b = a.axes
    b.set_xticklabels(b.get_xticklabels(), rotation=40, ha="right")
    plt.savefig('/var/www/www.tengagedblade.com/gift_data/' + user)

def main():
    form = cgi.FieldStorage()
    if "param1" in form:
        user = form["param1"].value
        giftplot(user)

cgitb.enable(display=0, logdir='./logs/')

