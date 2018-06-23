#!/usr/bin/python2.7

from multiprocessing import Pool
import urllib2
import re
import sys
from bs4 import BeautifulSoup
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import requests

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from CGIHTTPServer import CGIHTTPRequestHandler
import os
from time import sleep
import matplotlib
import cgitb
import cgi

cgitb.enable(display = 0, logdir = "./logs")
matplotlib.use('Agg')


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


def gameplot(user='alireza1373'):
    print(user)
    html = requests.get('https://tengaged.com/user/' + user).text
    karma, rank = re.findall('<span class="remark">(.*?)</span>', html)[0:2]

    soup = BeautifulSoup(html, 'html.parser')
    karma = soup.find(attrs={'class': 'remark'}).text
    #  rank = soup.find(attrs={'class': 'miniadrank'}).text
    games_played_default = soup.findAll(attrs={'class': 'remark'})[1].text;
    game_pages = int(soup.findAll(attrs={'class': 'page'})[3].text);
    last_activity = soup.findAll(attrs={'class': 'remark'})[2].text;

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
    plt.savefig('game_data/' + user)
    # plt.show()


def blogplot(user='ak73'):
    html = requests.get('https://tengaged.com/blog/' + user).text
    blogs_text = re.findall('<span class="info">(.*?)</span>', html)
    numblogs = filter(str.isdigit, blogs_text.__str__())
    soup = BeautifulSoup(html, 'html.parser')
    num_pages = (int(numblogs) / 6) +1
    page_blogs = soup.find(attrs={'class': 'blogPosts'})
    comments_db = pd.DataFrame(columns=['user', 'num_comments'])
    top_blog = 0
    blogs = page_blogs.findAll('a')

    for blog in blogs:
        if blog.has_attr('rel') and blog.attrs['rel'] and blog.attrs['rel'][0].startswith('bookmark'):
            blog_link = 'https://tengaged.com' + blog.attrs['href'].__str__()
            blog_html = requests.get(blog_link).text
            soup = BeautifulSoup(blog_html,"lxml")

            if re.findall('<span class="floated miniadrank">(.*?)</span>', blog_html):
                top_blog += 1

            comments = soup.findAll(attrs={'blogPostComments'})
            for comment in comments:
                tail = comment.find(attrs={'class': 'tail'})
                cuser = tail.find('a').text.__str__()
                if cuser in list(comments_db.user):
                    index = comments_db.user[(comments_db.user == cuser)].index[0]
                    current_count = comments_db.iloc[index].num_comments
                    comments_db.set_value(index, 'num_comments', current_count + 1)
                else:
                    comments_db = comments_db.append({'user': cuser, 'num_comments': 1}, ignore_index=True)

    blog_links = ('https://tengaged.com/blog/' + user + '/page/' + str(i) for i in range(1, num_pages + 1))
    ## first multi process
    p = Pool(processes=10)
    page_html = p.map(gethtml, blog_links)  ## passing blog_links as a generator
    p.close()
    blog_links = list()
    for html in page_html:
        soup = BeautifulSoup(html.text, "lxml")
        page_blogs = soup.find(attrs={'class': 'blogPosts'})
        blogs = page_blogs.findAll('a')
        for blog in blogs:
            if blog.has_attr('rel') and blog.attrs['rel'] and blog.attrs['rel'][0].startswith('bookmark'):
                blog_links += ['https://tengaged.com' + blog.attrs['href'].__str__()]

    p = Pool(processes=10)
    blot_html_all = p.map(gethtml, blog_links)# passing blog_links as a generator
    p.close()

    top_blog = 0
    comments = []
    for blog_html in blot_html_all:
        soup = BeautifulSoup(blog_html.text, "lxml")
        if re.findall('<span class="floated miniadrank">(.*?)</span>', blog_html.text):
            top_blog += 1

        comments += [soup.findAll(attrs={'blogPostComments'})]

    all_comments = (_ for blog_comment in comments for _ in blog_comment)

    for comment in all_comments:
        tail = comment.find(attrs={'class': 'tail'})
        cuser = tail.find('a').text.__str__()
        if cuser in list(comments_db.user):
            index = comments_db.user[(comments_db.user == cuser)].index[0]
            current_count = comments_db.iloc[index].num_comments
            comments_db.set_value(index, 'num_comments', current_count + 1)
        else:
            comments_db = comments_db.append({'user': cuser, 'num_comments': 1}, ignore_index=True)

    comments_db.num_comments = comments_db.num_comments.astype(int)
    top10 = (comments_db.nlargest(5, 'num_comments'))
    top_blog_percentage = 100 * (float(top_blog) / (num_pages * 6))


    a = sns.barplot(top10.user, top10.num_comments)
    a.set_title(user + '   top blog percentage:    ' + str(top_blog_percentage))
    b = a.axes
    b.set_xticklabels(b.get_xticklabels(), rotation=40, ha="right")
    plt.savefig('blog_data/' + user)

def gethtml(url, user_agent='tblade' , num_retries = 5):
    print('suc')
    headers = {'User-agent': user_agent}
    url_html = requests.get(url)
    if url_html.ok:
        return url_html
    elif url_html.error:
        print('Download error:', url_html.error.reason)
        if num_retries > 0:
            if hasattr(url_html.error, 'code') and 500 <= url_html.error.code < 600:
                # retry 5XX HTTP errors
                return gethtml(url, user_agent, num_retries - 1)




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
    top10 = (gifts_db.nlargest(10, 'num_gifts'))
    a = sns.barplot(top10.user, top10.num_gifts).set_title(user)
    b = a.axes
    b.set_xticklabels(b.get_xticklabels(), rotation=40, ha="right")
    plt.savefig('gift_data/' + user)


#blogplot('joe1110')
#gameplot('joe1110')
#if __name__ == '__main__':
#        cgitb.enable()
#        user = cgi.FieldStorage()
#        cgitb.enable(display=0, logdir='python/')
#        gameplot(user)



def run():
    server_address = ('35.196.36.213', 3000)
    httpd = HTTPServer(server_address, ScrapeHTTPRequestHandler)
    print(httpd)
    print('http server is running...')
    httpd.serve_forever()


# Create custom HTTPRequestHandler class
class ScrapeHTTPRequestHandler(CGIHTTPRequestHandler):
    # handle GET command
    def do_GET(self):
        rootdir = '/var/www/www.tengagedblade.com/scrape.py'  # file location
        try:
				os.mkdir('testo')
                print(user)
                user = self.path.split('/?mydata=')[1]
                gameplot(user)
                giftplot(user)
                blogplot(user)
                # send code 200 response
                self.send_response(200)

                # send file content to client
                return

        except IOError:
            self.send_error(404, 'file not found')


cgitb.enable(display=0, logdir='./logs/')

if __name_ == "__main_":
	form = cgi.FieldStorage()
	user = form.getlist("data") 
	os.mkdir('hi')
	print(user)
