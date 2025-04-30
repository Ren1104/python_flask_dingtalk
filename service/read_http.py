import sys
import os
from service.utils import Util
import time
import concurrent.futures

class readHttp:
    def __init__(self):
        pass
    def __build_prompt(self, text):
        prompt = f"""
        请对以下网页内容进行专业分析，提取核心信息：

        1. 主题：用一句话概括文章的核心主题（15字以内）
        2. 摘要：以有序列表形式提炼3-5个关键要点（每点15-20字）
        3. 思考：提供3-4条对该内容的见解或建议（总计不超过30字）

        输出格式要求：
        ### 主题
        [一句话概括主题]

        ### 摘要
        1. [要点一]
        2. [要点二]
        3. [要点三]
        ...

        ### 思考
        - [见解或建议]

        注意：
        - 总字数严格控制在100字以内
        - 保持客观专业的语言风格
        - 确保摘要涵盖文章最核心的信息
        - 不要包含无关内容或重复信息
        - 请你站在AI开发者或者AI创业者的角度提出思考或建议

        以下是网页内容：
        {text}
        """
        return prompt
    def __process_item(self, util, item):
        #处理单个新闻项目并返回结果
        try:
            url = item.get("url")
            title = item.get("title", "未知标题")
            # 获取网页内容
            text = util.read_http(url)
            if not text:
                return f"## {title}\n\n**URL**: {url}\n\n获取内容失败\n\n---\n\n"
            # 构建提示并调用LLM
            prompt = self.__build_prompt(text)
            model = "qwen-max"
            messages = [
                {"role": "system", "content": "你是一个专业的网页阅读助手，擅长分析网页内容后获取主题与摘要并提出自己的建议和思考。"},
                {"role": "user", "content": prompt}
            ]
            content = util.callLLM(model, messages)
            # 构建markdown格式的结果
            result = f"## {title}\n\n"
            result += f"**URL**: {url}\n\n"
            result += f"{content}\n\n"
            return result
        except Exception as e:
            return f"## 处理出错: {item.get('title', '未知标题')}\n\n**URL**: {item.get('url', '未知URL')}\n\n错误信息: {str(e)}\n\n---\n\n"

    def run_read_http(self):
        print(f"开始抓取和分析新闻...")
        start_time = time.time()

        util = Util()
        # 获取新闻列表
        try:
            news_items = util.scrape_aibase_news()
            if not news_items:
                print("未获取到任何新闻项目")
                return
                
            total_items = len(news_items)
            print(f"共获取到 {total_items} 条新闻")
            
            # 创建markdown文件头部
            markdown_content = f"# AI新闻摘要 ({time.strftime('%Y%m%d_%H%M%S')})\n\n"
            markdown_content += f"共 {total_items} 条新闻\n\n---\n\n"
            # 使用线程池并行处理新闻项目
            results = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                # 提交所有任务
                future_to_item = {
                    executor.submit(self.__process_item, util, item): (i, item) 
                    for i, item in enumerate(news_items)
                }
                
                # 收集结果（按原始顺序）
                for future in concurrent.futures.as_completed(future_to_item):
                    index, item = future_to_item[future]
                    try:
                        result = future.result()
                        results.append((index, result))
                    except Exception as e:
                        print(f"处理失败: {str(e)}")
                        results.append((index, f"## 处理失败\n\n错误: {str(e)}\n\n---\n\n"))
            
            # 按原始顺序写入文件
            results.sort(key=lambda x: x[0])
            for _, result in results:
                markdown_content += result
            
            total_time = time.time() - start_time
            print(f"处理完成! 总耗时: {total_time:.2f}秒")
            return markdown_content

        except Exception as e:
            print(f"发生错误: {str(e)}")
