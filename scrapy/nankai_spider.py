import scrapy
import os
from scrapy.http import HtmlResponse
from ..items import ItcastItem
from bs4 import BeautifulSoup

class ItcastSpider(scrapy.Spider):
    name = "itcast"
    allowed_domains = ["nankai.edu.cn"]
    start_urls = ["https://www.nankai.edu.cn/"]

    def __init__(self, *args, **kwargs):
        super(ItcastSpider, self).__init__(*args, **kwargs)
        self.item_count = 0  # 初始化计数器

    def parse(self, response):
        # 提取网页的 URL、标题、关键字、摘要
        items = []
        page_url = response.url
        page_title = response.xpath('//head/title/text()').get()
        page_keywords = response.xpath('//meta[@name="keywords"]/@content').get()
        page_description = response.xpath('//meta[@name="description"]/@content').get()

        # 使用BeautifulSoup解析HTML并提取纯文本内容
        soup = BeautifulSoup(response.text, 'lxml')
        page_text = soup.get_text(separator=' ', strip=True)  # 获取所有文本，用空格分隔，并去除多余空白

        # 提取页面中的所有链接
        #next_page_urls = [response.urljoin(next_page) for next_page in response.xpath('//a/@href').getall() if
                          #next_page]

        # 生成HTML文件名
        page_filename = self.generate_html_filename(page_url)
        self.save_html(page_url, response.text, page_filename)

        # 提取当前页面中的所有链接
        next_pages = []
        for next_page in response.xpath('//a/@href').getall():
            if next_page:
                next_page_url = response.urljoin(next_page)
                next_pages.append(next_page_url)

        # 增加计数器
        self.item_count += 1

        # 输出或保存数据
        yield {
            'seq': self.item_count,  # 添加序号
            'url': page_url,
            'title': page_title,
            'keywords': page_keywords,
            'description': page_description,
            'html_filename': page_filename,
            'links': next_pages,
            'content': page_text,  # 保存网页的完整 HTML 内容
            'pr': 0.3,
        }

        # 提取页面中的所有链接并继续爬取
        for next_page_url in next_pages:
            yield scrapy.Request(next_page_url, callback=self.parse)

    def save_html(self, url, content, filename):
        """
        保存网页内容为一个 HTML 文件
        :param url: 网页 URL
        :param content: 网页的 HTML 内容
        """
        # 获取网页的标题，并生成文件名
        # page_title = url.split('//')[1].replace('/', '_')  # 使用 URL 生成唯一文件名
        # file_name = f"{page_title}.html"

        # 创建保存文件的目录
        if not os.path.exists("html_files"):
            os.makedirs("html_files")

        # 将 HTML 内容写入文件
        with open(os.path.join("html_files", filename), 'w', encoding='utf-8') as file:
            file.write(content)

    def generate_html_filename(self, url):
        """
        根据URL生成HTML文件名
        :param url: 网页 URL
        :return: 生成的文件名
        """
        # 使用 URL 生成唯一文件名（这里可以根据需要修改生成规则）
        page_title = url.split('//')[1].replace('/', '_')
        return f"{page_title}.html"