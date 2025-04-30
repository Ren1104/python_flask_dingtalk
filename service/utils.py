import requests
from time import time
from bs4 import BeautifulSoup

'''
工具类
'''
class Util:
    '''
    调用大模型
    '''
    def callLLM(self, model, messages):
        try:
            # 通过HTTP请求调用通义API,支持指定model
            url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
            headers = {
                "Authorization": f"Bearer sk-2c7d7feddd254363b3b4f8491e2cc7c9",
                "Content-Type": "application/json"
            }
            start_time = time()
            payload = {
                "model": model,
                "input": {
                    "messages": messages
                },
            }
            response = requests.post(url, headers=headers, json=payload)
            end_time = time()
            print(f"大模型调用耗时:{end_time-start_time}")
            if response.status_code == 200:
                result = response.json()
                return result["output"]["text"]
            else:
                return f"分析失败: HTTP错误 {response.status_code}"
        except Exception as e:
            return f"分析失败: {str(e)}"

    '''
    读取器工具
    '''
    def read_http(self, url):
        # 替换原始url为读取器url
        start_time = time()
        target_url = f"https://r.jina.ai/{url}"
        headers = {
            "Authorization": "Bearer jina_9943c3148868428086aef9acc0a103d66RFF85N5BKmpdTA6Zomqdgn14634",
            "Content-Type": "application/json",
            "X-Engine": "browser"
        }
        response = requests.get(url=target_url, headers=headers)
        end_time = time()
        print(f"网页阅读耗时:{end_time - start_time}")
        return response.text

    '''
    爬取网页链接
    '''
    def scrape_aibase_news(self):
        url = 'https://www.aibase.com/zh/news'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        news_items = soup.find_all('a', class_='flex group justify-between md:flex-row flex-col-reverse hover:bg-[#F0F3FA] rounded-lg md:p-4 py-2 px-0 group')
        
        results = []
        for item in news_items[:5]:
            result = self.__parse_news_item(str(item))
            results.append(result)
        
        return results

    '''
    解析新闻项
    '''
    def __parse_news_item(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 查找a标签并获取href
        a_tag = soup.find('a')
        href = a_tag.get('href', '')
        full_url = f"https://www.aibase.com/zh{href}"
        
        # 获取h3标签的标题内容
        title = soup.find('h3', class_='line-clamp-2').text.strip()
        
        return {
            'url': full_url,
            'title': title
        }
