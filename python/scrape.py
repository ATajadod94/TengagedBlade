import urllib2
import re
from bs4 import BeautifulSoup
import pandas as pd
import seaborn as sns
import matplotlib as mpl
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
def gameplot(user = 'ak73'):
    html = download('https://tengaged.com/user/' + user)
    karma, rank = re.findall('<span class="remark">(.*?)</span>', html)[0:2]

    soup = BeautifulSoup(html, 'html.parser')
    karma = soup.find(attrs={'class': 'remark'}).text
    rank = soup.find(attrs={'class': 'miniadrank'}).text
    games_played_default = soup.findAll(attrs={'class': 'remark'})[1].text;
    game_pages = int(soup.findAll(attrs={'class': 'page'})[3].text);
    last_activity = soup.findAll(attrs={'class': 'remark'})[2].text;

    allgames = pd.DataFrame(columns=['type', 'placing'])

    for i in range(1, game_pages + 1):
        html = download('http://tengaged.com/user/' + user + '/ajax/search.json?action=loadGames&p=' + str(i) + '&uid=' + user)
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
    lm = sns.swarmplot(allgames.type, allgames.placing.astype(int), order = ['casting','fasting','rookies','frooks', 'survivor', 'hunger']).set_title(user)
    axes = lm.axes
    axes.set_yticks(range(1, 31))
    #plt.savefig(lm, format=format)
    plt.savefig('game_data/' + user)
    #plt.show()

gameplot('ak73')