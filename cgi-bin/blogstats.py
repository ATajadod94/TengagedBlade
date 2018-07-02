#!/usr/bin/python2.7

from multiprocessing import Pool
import os
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


def blogplot(user='ak73'):
    html = requests.get('https://tengaged.com/blog/' + user).text
    blogs_text = re.findall('<span class="info">(.*?)</span>', html)
    numblogs = filter(unicode.isdigit, blogs_text[0])
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

    blog_links = ('https://tengaged.com/blog/' + user + '/page/' + str(i) for i in range(1, max(20, num_pages + 1)))

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
    try:
        top10 = (comments_db.nlargest(5, 'num_comments'))
    except:
        top10 = comments_db

    top_blog_percentage = 100 * (float(top_blog) / (num_pages * 6))

    a = sns.barplot(top10.user, top10.num_comments)
    a.set_title(user + '   top blog percentage:    ' + str(top_blog_percentage))
    b = a.axes
    b.set_xticklabels(b.get_xticklabels(), rotation=40, ha="right")
    plt.savefig('/var/www/www.tengagedblade.com/blog_data/' + user)


def gethtml(url, user_agent='tblade' , num_retries = 5):
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

def main():
    form = cgi.FieldStorage()
    if "param1" in form:
        user = form["param1"].value
        if os.path.exists('blog_data/' + user):
            if os.path.getmtime('blog_data/' + user) < 1209600:
                blogplot(user[1::])
        print('blog_data/' + user)

cgitb.enable(display=0, logdir='./logs/')

#main()
print "Content-type: text/html\n"
print
main()
