from flask import Flask, request, jsonify
from service.github_read import GitHubAnalyzer
import logging

from service.read_http import readHttp

# 创建Flask应用实例
app = Flask(__name__)

@app.route('/')
def index():
    return "Max的Python后端服务"

@app.route('/api/news_analyze', methods=['GET'])
def read_http():
    reader = readHttp()
    markdown_content = reader.run_read_http()
    print(markdown_content)
    return markdown_content
if __name__ == '__main__':
    # 在开发环境中启动应用
    app.run(host='0.0.0.0', port=5000)