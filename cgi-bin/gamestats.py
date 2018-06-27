
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

def gameplot(user='alireza1373'):
    html = requests.get('https://tengaged.com/user/' + user).text
    ##karma, rank = re.findall('<span class="remark">(.*?)</span>', html)[0:2]
    soup = BeautifulSoup(html, 'html.parser')
    games_played_default = soup.findAll(attrs={'class': 'remark'})[1].text;
    karma = soup.find(attrs={'class': 'remark'}).text
    #  rank = soup.find(attrs={'class': 'miniadrank'}).text
    #last_activity = soup.findAll(attrs={'class': 'remark'})[2].text;

    game_pages = int(soup.findAll(attrs={'class': 'page'})[-1].text);

    allgames = pd.DataFrame(columns=['type', 'placing'])

    for i in range(1, game_pages + 1):
        html = requests.post('http://tengaged.com/user/' + user, {'action': 'loadGames', 'p': i, '&uid' : user})
        soup = BeautifulSoup(html.text, 'html.parser')
        games_in_page = soup.findAll(attrs={'class': 'game'})
        for agame in games_in_page:
            if agame.text.startswith('Enter'):
                continue
            placing = agame.find_all('a')[0].text
            placing = filter(str.isdigit, placing.__str__())
            fast = agame.attrs['class']

            fast = agame.text.__contains__('FF') or agame.text.__contains__('FDay')
            game = agame.find_all('a')[0].attrs['class'][0]
            if game.startswith('ghbut'):
                allgames = allgames.append({'type': 'hunger', 'placing': int(placing)}, ignore_index=True)
            if game.startswith('gsvbut'):
                allgames = allgames.append({'type': 'survivor', 'placing': int(placing)}, ignore_index=True)
            if game.startswith('grbut'):
                if fast:
                    allgames = allgames.append({'type': 'frooks', 'placing': int(placing)}, ignore_index=True)
                else:
                    allgames = allgames.append({'type': 'rookies', 'placing': int(placing)}, ignore_index=True)
            if game.startswith('gbut'):
                if fast:
                    allgames = allgames.append({'type': 'fasting', 'placing': int(placing)}, ignore_index=True)
                else:
                    allgames = allgames.append({'type': 'casting', 'placing': int(placing)}, ignore_index=True)
            if game.startswith('gsbut'):
                allgames = allgames.append({'type': 'stars', 'placing': int(placing)}, ignore_index=True)

    realgames = allgames.__len__()
    lm = sns.swarmplot(allgames.type, allgames.placing.astype(int),
                       order=['casting', 'fasting', 'rookies', 'frooks', 'survivor', 'hunger', 'stars']).set_title(user)
    axes = lm.axes
    axes.set_yticks(range(1, 31))
    # plt.savefig(lm, format=format)
    plt.savefig('/var/www/www.tengagedblade.com/game_data/' + user)
    # plt.show()

def main():
    form = cgi.FieldStorage()
    if "param1" in form:
        user = form["param1"].value
        gameplot(user)

cgitb.enable(display=0, logdir='./logs/')

main()
print "Content-type: text/xml"
print
print "<?xml version='1.0'?>"
print "<names>"
print "\t<name>"
print "\t\t<first>Alpha</first>"
print "\t\t<last>Delta</last>"
print "\t</name>"
print "\t<name>"
print "\t\t<first>Bravo</first>"
print "\t\t<last>Omega</last>"
print "\t</name>"
