# coding=utf-8
import cookielib
import getopt
import ssl
import sys
import urllib2
from datetime import datetime
from time import sleep

from lxml import etree

KEY_WORD = ''

TARGET_URL = ''

BASE_SLEEP_TIME = 2  # 基本延迟时间

INTERVAL_TIME = 20  # 间隔时间

MAX_PAGE = 10

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36'

'''
百度搜索接口参数说明

ie:关键字编码格式默认为：GB2312 简体中文


f: 值有：1，3，8大概还有其他的，临时发现就这3种，
1指的是相干搜索，透露表现用户选择了搜索页面最下面的“相干搜索”中的某个关键词。；
3下拉框搜索透露表现用户输入肯定的词语之后出现“联想词语”，用户最终用鼠标选择了某个关键词；或用键盘选择了某个关键词后直接按回车。；
8用户自立搜索，透露表现用户直接点击“百度一下”按键（有bs变量时才出现f=8）


rsv_bp:使用的是百度哪一个搜索框0是首页输入；1是顶部搜索输入；2是底部搜索输入

rsv idx：未知

rsv_pq：透露表现用来记录关键词和上一次搜素的关键词（相干关键词）的

tn: 提交搜索请求来源

wd:查询关键字 (word) 一般以也会是一串字符

rsv_t：搜索效果的一种随机密码

rqlang：跟地域有关cn是代表中国地域

rsv_enter：未知

rsv_sug: 0 搜索框提示0条搜索历史记录1 搜索框提示1条搜索历史记录2 搜索框提示2条搜索历史记录

'''


def logger(msg, level='INFO'):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print >> sys.stdout, '[%s] %s %s' % (now, level, msg)


def init():
    logger('启动脚本')
    logger('初始化配置')
    ssl._create_default_https_context = ssl._create_unverified_context
    cookie = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
    urllib2.install_opener(opener)


def open_baidu():
    logger('打开百度')
    try:
        req = urllib2.Request('https://www.baidu.com/')
        req.add_header('User-Agent', UA)
        resp = urllib2.urlopen(req)
    except Exception, e:
        logger(e)
    start_sleep(BASE_SLEEP_TIME)


def search_key():
    logger('开始搜索关键词:%s' % KEY_WORD)
    logger('打开搜索结果第1页')
    url = 'https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=0&rsv_idx=1&tn=baidu&wd=%s&rsv_pq=8f2c01fc00021f09&rqlang=cn&rsv_enter=1&rsv_sug3=2' % KEY_WORD
    refer = 'https://www.baidu.com/'
    data = open_url(url, refer)
    find_target(1, url, data)


def find_target(page, requestUrl, data):
    target_url = TARGET_URL[:15]
    tree = etree.HTML(data)
    notes = tree.xpath('//div[@class="result c-container "]')
    index = 0
    for note in notes:
        index += 1
        urls = note.xpath('div/div/div[@class="f13"]/a/text()|div[@class="f13"]/a/text()')
        
        if not urls:
            continue
        url = urls[0]
        
        if url.startswith(target_url):
            logger('匹配成功')
            logger('当前目标所在位置:第%d页 第%d条' % (page, index))
            ret = note.xpath('h3/a/@href')[0]
            logger('目标链接:%s' % ret)
            logger('打开目标链接')
            open_url(ret, requestUrl)
            logger('脚本执行完成')
            exit()
    
    logger('匹配失败')
    
    cPage = tree.xpath('//div[@id="page"]/strong/span/text()')[0]
    
    nextPage = int(cPage) + 1
    
    if nextPage > MAX_PAGE:
        logger('执行到最大页码数,无匹配结果,停止脚本')
        exit()
    
    links = tree.xpath('//div[@id="page"]/a[@class="n"]')
    
    for link in links:
        if u'下一页' in link.xpath('text()')[0]:
            start_sleep(BASE_SLEEP_TIME)
            nextPageUrl = 'https://www.baidu.com%s' % link.xpath('@href')[0]
            logger('打开搜索结果第%d页' % nextPage)
            data = open_url(nextPageUrl, requestUrl)
            find_target(nextPage, nextPageUrl, data)
    
    logger('执行到最后一页,无匹配结果,停止脚本')


def open_url(url, refer):
    try:
        req = urllib2.Request(url)
        req.add_header('User-Agent', UA)
        req.add_header('Referer', refer)
        resp = urllib2.urlopen(req)
        return resp.read()
    except Exception, e:
        logger(e)


def start_sleep(time):
    logger('休眠%ds...' % time)
    sleep(time)


def get_param():
    key = ''
    url = ''
    opts, args = getopt.getopt(sys.argv[1:], "k:u:")
    for op, value in opts:
        if op == "-k":
            key = value
        elif op == "-u":
            url = value

    if not key:
        print ("请传入关键字 例: -k '哈哈'")
        exit()
    
    if not url:
        print ("请传入目标URL 例: -u 'game.3533.com'")
        exit()

    logger('当前关键字:%s 目标链接:%s' % (key, url))
    
    global KEY_WORD
    KEY_WORD = key
    global TARGET_URL
    TARGET_URL = url


if __name__ == '__main__':
    get_param()
    init()
    open_baidu()
    search_key()
