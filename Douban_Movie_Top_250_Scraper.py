import re

import requests
from bs4 import BeautifulSoup
import time
import csv
import random


class Douban_Movie_Top_250_Scraper:
    def __init__(self):
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"}
        self.url = "https://movie.douban.com/top250"
        self.movies = []

    # 获取页单数据
    def get_page(self, start=0):
        params = {'start': start}
        try:
            response = requests.get(self.url, params=params, headers=self.headers, timeout=5)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text
        except requests.Timeout:
            print("请求超时！")
        except requests.ConnectionError:
            print("连接错误！")
        except requests.RequestException as e:
            print(f'请求失败：{e}')
            return None

    # 解析页面
    def parse_page(self, html):
        soup = BeautifulSoup(html, 'lxml')
        movie_items = soup.find_all('div', class_='item')

        for item in movie_items:
            movie = {}

            # 电影名称
            title = item.find('span', class_='title')
            movie['电影名称'] = title.text if title else 'NAN'

            # 电影信息
            bd = item.find('div', class_='bd')
            if bd:
                info = bd.find('p').text.strip()
                pattern = r'导演:\s*([^主演]+?)\s*主演:\s*(.+?)(?:\s|$)'
                match = re.search(pattern, info)
                if match:
                    movie['导演'] = match.group(1).strip()
                    movie['主演'] = match.group(2).strip()
            # 评分
            rating_num = item.find('span', class_='rating_num')
            movie['评分'] = rating_num.text if rating_num else 'NAN'

            # 评价人数
            rate_nums = item.select_one('div.info div.bd div span:nth-of-type(4)')
            movie['评价人数'] = rate_nums.text if rate_nums else 'NAN'

            # 评价
            quote = item.select_one('div.info div.bd p.quote span')
            movie['quote'] = quote.text if quote else 'NAN'

            # 图片
            pic = item.select_one('div.pic a img')
            movie['pic'] = pic.get("src") if pic else 'NAN'

            self.movies.append(movie)

        # 保存在csv文件里
    def save_to_csv(self):
        if not self.movies:
            print("未获取到数据，请检查程序是否故障！")
            return None
        filename = 'Douban_Movie_Top_250.csv'
        with open(filename, 'w', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.movies[0].keys())
            writer.writeheader()
            writer.writerows(self.movies)
        print(f'数据已经保存到{filename}')

    # 运行
    def run(self):
        print("开始爬取豆瓣电影Top250，请稍后...")
        for page in range(0, 250, 25):
            print(f'正在爬取第{page // 25 + 1}页》》》')
            html = self.get_page(page)
            if html:
                self.parse_page(html)
            # 随即休眠，避免被封
            time.sleep(random.uniform(1, 3))

        self.save_to_csv()
        print(f'爬取完成，共获取{len(self.movies)}部电影！')


if __name__ == '__main__':
    spider = Douban_Movie_Top_250_Scraper()
    spider.run()
