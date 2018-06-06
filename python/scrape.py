import urllib2
import re
from bs4 import BeautifulSoup
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt


def download(url, user_agent='wswp', num_retries=2):
    print 'Downloading:', url
    headers = {'User-agent': user_agent}
    request = urllib2.Request(url, headers=headers)
    try:
        html = urllib2.urlopen(request).read()
    except urllib2.URLError as e:
        print 'Download error:', e.reason
        html = None
        if num_retries > 0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                # retry 5XX HTTP errors
                return download(url, user_agent, num_retries - 1)
    return html


def gameplot(user='alireza1373'):
    html = download('https://tengaged.com/user/' + user)
    karma, rank = re.findall('<span class="remark">(.*?)</span>', html)[0:2]

    soup = BeautifulSoup(html, 'html.parser')
    karma = soup.find(attrs={'class': 'remark'}).text
    #  rank = soup.find(attrs={'class': 'miniadrank'}).text
    games_played_default = soup.findAll(attrs={'class': 'remark'})[1].text;
    game_pages = int(soup.findAll(attrs={'class': 'page'})[3].text);
    last_activity = soup.findAll(attrs={'class': 'remark'})[2].text;

    allgames = pd.DataFrame(columns=['type', 'placing'])

    for i in range(1, game_pages + 1):
        html = download(
            'http://tengaged.com/user/' + user + '/post/search.json?action=losdadaadGames&p=' + str(i) + '&uid=' + user)
        soup = BeautifulSoup(html, 'html.parser')
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
    html = download('https://tengaged.com/blog/' + user)
    blogs_text = re.findall('<span class="info">(.*?)</span>', html)
    numblogs = filter(str.isdigit, blogs_text.__str__())
    soup = BeautifulSoup(html, 'html.parser')
    num_pages = (int(numblogs) / 6) + 1
    page_blogs = soup.find(attrs={'class': 'blogPosts'})
    comments_db = pd.DataFrame(columns=['user', 'num_comments'])
    top_blog = 0

    blogs = page_blogs.findAll('a')

    for blog in blogs:
        if blog.has_attr('rel') and blog.attrs['rel'] and blog.attrs['rel'][0].startswith('bookmark'):
            blog_link = 'https://tengaged.com' + blog.attrs['href'].__str__()
            blog_html = download(blog_link)
            soup = BeautifulSoup(blog_html)

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

    for i in range(2, min(num_pages + 1, 2000)):
        link = 'https://tengaged.com/blog/' + user + '/page/' + str(i)
        html = download(link)
        soup = BeautifulSoup(html)

        page_blogs = soup.find(attrs={'class': 'blogPosts'})
        blogs = page_blogs.findAll('a')

        for blog in blogs:
            if blog.has_attr('rel') and blog.attrs['rel'] and blog.attrs['rel'][0].startswith('bookmark'):
                blog_link = 'https://tengaged.com' + blog.attrs['href'].__str__()
                blog_html = download(blog_link)
                soup = BeautifulSoup(blog_html)

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
    comments_db.num_comments = comments_db.num_comments.astype(int)
    top10 = (comments_db.nlargest(20, 'num_comments'))
    top_blog_percentage = 100 * (float(top_blog) / (i * 6))
    a = sns.barplot(top10.user, top10.num_comments).set_title(
        user + '   top blog percentage:    ' + str(top_blog_percentage))
    b = a.axes
    b.set_xticklabels(b.get_xticklabels(), rotation=40, ha="right")
    plt.savefig('blog_data/' + user)


def giftplot(user='ak73'):
    html = download('https://tengaged.com/gifts/' + user)
    num_gifts = re.findall('<span class="remark">(.*?)</span>', html)[0]
    num_pages = np.ceil(float(num_gifts) / 15)
    soup = BeautifulSoup(html, 'html.parser')
    gifts_db = pd.DataFrame(columns=['user', 'num_gifts'])

    for i in range(1, int(num_pages) + 1):
        html = download(
            'http://tengaged.com/gifts/' + user + '/ajax/search.json?action=loadGifts&p=2')
        soup = BeautifulSoup(html, 'html.parser')
        gifts = soup.findAll(attrs={'class': 'gifts imgMsgList big'})[0]
        gifters = gifts.findAll(attrs={'class': 'message'})
        for gifter in gifters:
            cuser = gifter.find_all('a')[0].text.__str__()
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

#gameplot('Arris')
blogplot('KatarinaDuCouteau')
#giftplot('lemonface')
