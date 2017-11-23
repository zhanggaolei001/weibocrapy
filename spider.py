from urllib import request,parse
from lxml import etree
import re
import sqlite3
import string
def getHtml(url):
    print(url)
    page = request.urlopen(url)
    html = page.read()
    html=html.replace(r"\/".encode(), r"/".encode())
    return html

def save(dbconn, links):
    for link in links:
        fileLink=''.join(link)
        URIFileName=re.findall(r'(?<=l30zoo1wmz&fn=).*(?=&skiprd)',fileLink)[0]
        fileName=""
        try:
            fileName=parse.unquote(URIFileName)
        except:
            print('反转码失败')
            fileName=URIFileName
        c = dbconn.cursor()
        try:
            sqlStr="INSERT INTO File (FILENAME,FILEURL) VALUES (\"%s\",\"%s\")"%(fileName ,fileLink )
            print(sqlStr)
            c.execute(sqlStr)
        except:
            print('插入失败：'+fileName)
    dbconn.commit()
    print('成功插入：'+str(len(links))+'条数据')


def getScript(html):
    root = etree.HTML(html)
    xpathStr = "/html/body/div[2]/div[2]/div[2]/div[1]/script/text()"
    scriptStr = root.xpath(xpathStr)
    scriptStr=''.join(scriptStr)
    print(type(scriptStr))
    print(scriptStr)
    return scriptStr


def AnalyzeScriptToURLList(scriptStr):
    # 将正则表达式编译成Pattern对象
    #pattern = re.compile(r'url":"(http://file3)(.+?)"')
    links= re.findall(r'url":"(http://file3)(.*?)"', scriptStr, re.S)
    for link in links:
        link="".join(link)
        #print(link)
    return links

def getUrlList(html):
    scriptStr=getScript(html)
    return AnalyzeScriptToURLList(scriptStr)

listToBeCrap=["http://vdisk.weibo.com/s/zJQeg4_RkvSaa?sudaref=vdisk.weibo.com"]
crappedList=[]
def getOtherFileFolder(html,count):
    root = etree.HTML(html)
    xpathStr = r'//*[@id="fileListBody"]'
    if  not root.xpath(xpathStr):
        return
    newElementList = (root.xpath(xpathStr)[0]).getchildren()
    temList=[]
    for element in newElementList:
        #print('开始查找a标签')
        newUrl=element.findall('.//a[@class="short_name"]')[0].get('href')
        print('新加入网址：'+newUrl)
        temList.append(newUrl)
        #print(temList)
        #print(help(type(element)))
        #print('#######################################')

        #listToBeCrap.__add__(element)
    countOfList=len(temList)
    countOfCopy=countOfList-count
    return temList[0:countOfCopy]
#性能可提高：改为并发执行
i=0
conn = sqlite3.connect('test.db')
print ("Opened database successfully")
c=conn.cursor()
conn.commit()
try:
    c.execute('''CREATE TABLE File 
                (FILENAME TEXT PRIMARY KEY NOT NULL,
                FILEURL TEXT NOT NULL);''')
    conn.commit()
except sqlite3.OperationalError:
    print('table File already exists')


while len(listToBeCrap)>0:
    i+=1
    print('待爬取URL数量：' + str(len(listToBeCrap)) + '个')
    print('开始爬取第：'+str(i)+'个URL')
    #print(listToBeCrap)
    url=listToBeCrap.pop()
    html = getHtml(url)
    #print('getHtml结束')
    crappedList.append(url)
    #print(crappedList)
    urlList=getUrlList(html)
    count=len(urlList)
    #print('getUrlList结束')
    newFolderUrl=getOtherFileFolder(html, count)
    if  newFolderUrl:
        for folderUrl in newFolderUrl:
            if not (listToBeCrap.__contains__(folderUrl) or (crappedList.__contains__(folderUrl))):
                listToBeCrap.append(folderUrl)
    save(conn, urlList)
conn.close()