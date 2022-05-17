import json
import requests
import lxml.etree


def submit_to_baidu(api_url, urls):
    """
    Submit the url to baidu
    """

    headers = {
        'User-Agent': 'curl/7.12.1',
        'Host': 'data.zz.baidu.com',
        'Content-Type': 'text/plain',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Content-Length': str(len(urls))
    }

    res = requests.post(api_url, headers=headers, data=urls)
    return res.text


def get_urls(sitemap_url):
    """
    Get the urls from sitemap
    """

    res = requests.get(sitemap_url)

    tree = lxml.etree.fromstring(res.text.encode('utf-8'))

    namespaces = {
        'sitemapindex': 'http://www.sitemaps.org/schemas/sitemap/0.9',
    }

    urls = ''
    for url in tree.xpath("//sitemapindex:loc/text()", namespaces=namespaces):
        urls += url + '\n'

    return urls


if __name__ == '__main__':
    config = json.load(open('./baidu.json', 'r'))

    urls = get_urls(config['sitemap_url'])

    print(urls)

    print(submit_to_baidu(config['api_url'], urls))
