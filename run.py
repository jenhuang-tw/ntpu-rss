import requests, sys, datetime, time, json, re

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

    post_data = { "query": f"""
        {{
        publications(
            sort: "publishAt:desc,createdAt:desc"
            start: 0
            limit: 20
            where: {{
            isEvent: false
            sitesApproved_contains: "www_ntpu", "internal_ntpu", "law_ntpu", "cic_ntpu"
            lang_ne: "english"
            tags_contains: [[]]
            publishAt_lte: "{now_time}" 
            unPublishAt_gte: "{now_time}" 
            }}
        ) {{
            _id
            createdAt
            title
            
            title_en
            
            tags
            coverImage {{
            url
            }}
            coverImageDesc
            coverImageDesc_en
            bannerLink
            files {{
            url
            name
            mime
            }}
            fileMeta
            publishAt
            contactPerson
        }}
        }}
        """ 
        }

    r = requests.post('https://api-carrier.ntpu.edu.tw/strapi', data = post_data)

    obj = json.loads(r.text)
    news_json = obj['data']['publications']

    # SET List
    for news in news_json:
        setDetails(news)

def setDetails(news):
    # PUT Vulnerability Details
    title = news['title']
    if title == "":
        return "no"
    link = "https://new.ntpu.edu.tw/news/" + news['_id']

    desTag = ""
    if (news['tags'] != None) and (len(news['tags']) != 0):
        desTag1 = ", 🏷️ "
        desTag2 = ",".join ( news['tags'] )
        desTag = desTag1 + desTag2
    
    desContact = "無聯絡人資訊"
    if news['contactPerson'] != "":
        desContact = re.sub(r'\d+', '', news['contactPerson']) # Remove digits
        desContact = desContact.replace(" ","") # Remove whitespace
        desContact = desContact.replace("分機","").replace("#","").replace("、","").replace("；","") # Remove phone
    
    description = "🪶 "+desContact  + desTag + "."
    pubDate = datetime.datetime.strptime(news['publishAt'], '%Y-%m-%dT%H:%M:%S.000Z').strftime(GMT_FORMAT)
    items.append( item(title, link, description, pubDate) )

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
                    r'<pubDate>{}</pubDate>' \
                    r'<description>{}</description>' \
                    r'<link>{}</link>' \
                    r'</item>' \
                    "\n" \
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
