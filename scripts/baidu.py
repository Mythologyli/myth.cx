import sys
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


def get_urls(sitemap_path):
    """
    Get the urls from sitemap
    """

    tree = lxml.etree.parse(sitemap_path)

    namespaces = {
        'sitemapindex': 'http://www.sitemaps.org/schemas/sitemap/0.9',
    }

    urls = ''
    for url in tree.xpath("//sitemapindex:loc/text()", namespaces=namespaces):
        urls += url + '\n'

    return urls


if __name__ == '__main__':
    urls = get_urls(sys.argv[1])

    print(urls)

    print(submit_to_baidu(sys.argv[2], urls))
