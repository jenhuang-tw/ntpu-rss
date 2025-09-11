import requests, sys, datetime, time, json, html
from bs4 import BeautifulSoup

# GMT Format
GMT_FORMAT =  '%a, %d %b %Y %H:%M:%S GMT'

# rss channel
class channel(object):

    def __init__(self, title, author, image, link, description, language, copyright):
        self.title = title
        self.author = author
        self.image = image
        self.link = link
        self.description = description
        self.language = language
        self.copyright = copyright

# rss item
class item(object):

    def __init__(self, title, pubDate, description, link):
        self.title = title
        self.link = link
        self.description = description
        self.pubDate = pubDate

def getChannel():
    # GET XML Channel
    title = "臺北大學校首頁"
    author = "NTPU 國立臺北大學"
    image = "https://new.ntpu.edu.tw/assets/logo/ntpu_logo.png"
    link = "https://new.ntpu.edu.tw/news"
    description = "臺北大學校首頁公告（含各單位）"
    language = "zh_TW"
    copyright = "NTPU 國立臺北大學 - 首頁公告"
    print("+ [1] Create XML Channel")
    return channel(title, author, image, link, description, language, copyright)

def getItem():
    now_time = str(time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.localtime()))
    post_data = {
        "query": "{\npublications(\nsort: \"publishAt:desc,createdAt:desc\"\nstart: 0\nlimit: 20\nwhere: {\n  isEvent: false\n  sitesApproved_contains: \"www_ntpu\"\n  \n  lang_ne: \"english\"\n  tags_contains: [[]]\n  \n  publishAt_lte: \"" + now_time + "\" unPublishAt_gte: \"" + now_time + "\" \n}\n    ) {\n_id\ncreatedAt\ntitle\ncontent\ntitle_en\ncontent_en\ntags\ncoverImage {\n  url\n}\ncoverImageDesc\ncoverImageDesc_en\nbannerLink\nfiles {\n  url\n  name\n  mime\n}\nfileMeta\npublishAt\n    }}"
    }
    r = requests.post('https://api-carrier.ntpu.edu.tw/strapi', data = post_data)

    obj = json.loads(r.text)
    news_json = obj['data']['publications']

    # SET List
    for news in news_json:
        setDetails(news)

def cleanMe(html):
    soup = BeautifulSoup(html, "html.parser") # create a new bs4 object from the html data loaded
    for script in soup(["script", "style"]): # remove all javascript and stylesheet code
        script.extract()
    # get text
    text = soup.get_text()
    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    return text

def setDetails(news):
    # PUT Vulnerability Details
    title = news['title']
    if title == "":
        return "no"
    link = "https://new.ntpu.edu.tw/news/" + news['_id']
    description = news['content'].replace("<p>&nbsp;</p>", "").replace("<o:p>", "<p>").replace("</o:p>", "</p>").replace("color=black", "color=\"black\"").replace("&nbsp;", "").replace("&", "-")
    pubDate = datetime.datetime.strptime(news['publishAt'], '%Y-%m-%dT%H:%M:%S.000Z').strftime(GMT_FORMAT)
    items.append(item(title, link, cleanMe(html.unescape(description)), pubDate))

def createRSS(channel):
    
    # XML Format - XML Channel
    rss_text = r'<rss ' \
               r'version="2.0" ' \
               r'encoding="UTF-8">' \
               r'<channel>' \
               r'<title>{}</title>' \
               r'<link>{}</link>' \
               r'<description>{}</description>' \
               r'<author>{}</author>' \
               r'<image>' \
               r'<url>{}</url>' \
               r'</image>' \
               r'<language>{}</language>' \
               r'<copyright>{}</copyright>' \
        .format(channel.title, channel.link, channel.description ,channel.author, channel.image, channel.language, channel.copyright)

    # XML Format - XML Items
    for item in items:
        rss_text += r'<item>' \
                    r'<title>{}</title>' \
                    r'<link>{}</link>' \
                    r'<description>{}</description>' \
                    r'<pubDate>{}</pubDate>' \
                    r'</item>' \
            .format(item.title, item.pubDate, item.description, item.link)

    rss_text += r'</channel></rss>'

    # Write File 
    FileName = "NTPU_News.xml"
    with open(FileName, 'w', encoding = 'utf8') as f:
        f.write(rss_text)
        f.flush()
        f.close
    print("+ [2] GET XML File")

if __name__=="__main__":
    # PUT Vulnerability Details
    items = []

    # 1. Channel
    channel_ = getChannel()
    # 2. Items
    getItem()
    # 3. Create RSS
    createRSS(channel_)
