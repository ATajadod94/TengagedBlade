#!/usr/bin/python2.7

import requests
from bs4 import BeautifulSoup
import cgitb
import cgi


def basestats(user):
    html = requests.get('https://tengaged.com/user/' + user).text
    soup = BeautifulSoup(html, 'html.parser')
    avi = [x['src'] for x in soup.findAll('img', {'class': 'avatarpic'})][0]
    karma = soup.find(attrs={'class': 'remark'}).text
    games_played_default = soup.findAll(attrs={'class': 'remark'})[1].text;

    print str(avi), int(karma), int(games_played_default), int(karma)/int(games_played_default)

def main():
    form = cgi.FieldStorage()
    if "param1" in form:
        user = form["param1"].value
        basestats(user)


cgitb.enable(display=0, logdir='./logs/')

print "Content-type: text/html\n"
print
main()
