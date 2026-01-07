"""
Flask API路由
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from app.core.research_assistant import ResearchAssistant
from flask import render_template
#
#
# def create_app(assistant: ResearchAssistant):
#     """创建Flask应用"""
#     app = Flask(__name__)
#     CORS(app)
#
#     @app.route('/')
#     def index():
#         """返回前端页面"""
#         return render_template('index.html')
#
#     # ... 保持其他API路由不变
# #
# # def create_app(assistant: ResearchAssistant):
# #     """创建Flask应用"""
# #     app = Flask(__name__)
# #     CORS(app)
#
#     @app.route('/api/ask', methods=['POST'])
#     def ask():
#         """问答接口"""
#         data = request.json
#         question = data.get('question', '')
#
#         if not question:
#             return jsonify({'error': '问题不能为空'}), 400
#
#         answer = assistant.ask(question)
#         return jsonify({'answer': answer})
#
#     @app.route('/api/analyze_similarity', methods=['POST'])
#     def analyze_similarity():
#         """相似性分析接口"""
#         result = assistant.analyze_similarity()
#         return jsonify({'result': result})
#
#     @app.route('/api/recommend', methods=['POST'])
#     def recommend():
#         """研究推荐接口"""
#         result = assistant.recommend_research()
#         return jsonify({'result': result})
#
#     @app.route('/api/documents', methods=['GET'])
#     def get_documents():
#         """获取文档列表"""
#         documents = assistant.get_document_list()
#         return jsonify({'documents': documents})
#
#     @app.route('/api/status', methods=['GET'])
#     def status():
#         """获取状态"""
#         return jsonify({
#             'indexed': assistant.is_indexed,
#             'document_count': len(assistant.documents_text)
#         })
#
#     return app
#
def create_app(assistant: ResearchAssistant):
    """创建Flask应用"""
    app = Flask(__name__)
    CORS(app)

    @app.route('/')
    def home():  # 修改函数名
        """返回前端页面"""
        return '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>个人科研助手</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { opacity: 0.9; font-size: 1.1em; }
        .content { padding: 30px; }
        .status-bar {
            background: #f5f5f5;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .status-item { display: flex; align-items: center; gap: 10px; }
        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #4caf50;
        }
        .status-dot.inactive { background: #f44336; }
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }
        .tab {
            padding: 12px 24px;
            cursor: pointer;
            border: none;
            background: none;
            font-size: 1em;
            color: #666;
            transition: all 0.3s;
            border-bottom: 3px solid transparent;
        }
        .tab.active {
            color: #667eea;
            border-bottom-color: #667eea;
            font-weight: bold;
        }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .input-group { margin-bottom: 20px; }
        .input-group label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
        }
        .input-group textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 1em;
            resize: vertical;
            font-family: inherit;
        }
        .input-group textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        .button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 8px;
            font-size: 1em;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        .button:active { transform: translateY(0); }
        .button:disabled { opacity: 0.6; cursor: not-allowed; }
        .result-box {
            margin-top: 20px;
            padding: 20px;
            background: #f9f9f9;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            min-height: 100px;
            white-space: pre-wrap;
            line-height: 1.6;
        }
        .loading {
            text-align: center;
            padding: 20px;
            color: #666;
        }
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .documents-list {
            list-style: none;
            padding: 0;
        }
        .documents-list li {
            padding: 10px;
            background: #f5f5f5;
            margin-bottom: 10px;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔬 个人科研助手</h1>
            <p>基于AI的本地科研文档分析系统</p>
        </div>
        <div class="content">
            <div class="status-bar">
                <div class="status-item">
                    <span class="status-dot" id="statusDot"></span>
                    <span id="statusText">检查状态...</span>
                </div>
                <div id="documentCount">文档数: 0</div>
            </div>
            <div class="tabs">
                <button class="tab active" onclick="switchTab('qa')">文档问答</button>
                <button class="tab" onclick="switchTab('similarity')">相似性分析</button>
                <button class="tab" onclick="switchTab('recommend')">研究推荐</button>
                <button class="tab" onclick="switchTab('web')">联网模式</button>
                <button class="tab" onclick="switchTab('documents')">文档列表</button>
            </div>
            <div id="qa" class="tab-content active">
                <div class="input-group">
                    <label for="question">请输入您的问题：</label>
                    <textarea id="question" rows="3" placeholder="例如：这篇文档的主要研究方法是什么？"></textarea>
                </div>
                <button class="button" onclick="askQuestion()">提问</button>
                <div id="qaResult" class="result-box" style="display: none;"></div>
            </div>
            <div id="similarity" class="tab-content">
                <p style="margin-bottom: 20px;">分析多个文档在研究问题、方法和思路上的相似性</p>
                <button class="button" onclick="analyzeSimilarity()">开始分析</button>
                <div id="similarityResult" class="result-box" style="display: none;"></div>
            </div>
            <div id="recommend" class="tab-content">
                <p style="margin-bottom: 20px;">基于现有文档推荐研究问题和方法</p>
                <button class="button" onclick="recommendResearch()">获取推荐</button>
                <div id="recommendResult" class="result-box" style="display: none;"></div>
            </div>
            <div id="web" class="tab-content">
                <div class="input-group">
                    <label for="webUrl">请输入网页URL（支持DeepSeek对话等）：</label>
                    <input type="text" id="webUrl" placeholder="https://..." style="width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 1em;">
                </div>
                <div class="input-group">
                    <label for="webFocus">总结重点（可选）：</label>
                    <input type="text" id="webFocus" placeholder="例如：复习总结、关键知识点等" value="复习总结" style="width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 1em;">
                </div>
                <button class="button" onclick="fetchAndSummarize()">抓取并总结</button>
                <div id="webResult" class="result-box" style="display: none;"></div>
                <div style="margin-top: 20px;">
                    <h3 style="margin-bottom: 10px;">已抓取的网页：</h3>
                    <ul class="documents-list" id="webContentsList"></ul>
                </div>
            </div>
            <div id="documents" class="tab-content">
                <h3 style="margin-bottom: 15px;">已加载的文档：</h3>
                <ul class="documents-list" id="documentsList"></ul>
            </div>
        </div>
    </div>
    <script>
        const API_BASE = '/api';

        async function checkStatus() {
            try {
                const response = await fetch(`${API_BASE}/status`);
                const data = await response.json();
                const statusDot = document.getElementById('statusDot');
                const statusText = document.getElementById('statusText');
                const documentCount = document.getElementById('documentCount');

                if (data.indexed) {
                    statusDot.classList.remove('inactive');
                    statusText.textContent = '系统已就绪';
                } else {
                    statusDot.classList.add('inactive');
                    statusText.textContent = '系统未初始化';
                }
                documentCount.textContent = `文档数: ${data.document_count || 0} | 网页数: ${data.web_content_count || 0}`;
                if (data.indexed) {
                    loadDocuments();
                    loadWebContents();
                }
            } catch (error) {
                console.error('状态检查失败:', error);
            }
        }

        async function loadDocuments() {
            try {
                const response = await fetch(`${API_BASE}/documents`);
                const data = await response.json();
                const list = document.getElementById('documentsList');
                list.innerHTML = '';
                if (data.documents.length === 0) {
                    list.innerHTML = '<li>暂无文档</li>';
                } else {
                    data.documents.forEach(doc => {
                        const li = document.createElement('li');
                        li.textContent = doc;
                        list.appendChild(li);
                    });
                }
            } catch (error) {
                console.error('加载文档列表失败:', error);
            }
        }

        function switchTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
            if (tabName === 'documents') {
                loadDocuments();
            } else if (tabName === 'web') {
                loadWebContents();
            }
        }

        async function askQuestion() {
            const question = document.getElementById('question').value.trim();
            if (!question) {
                alert('请输入问题');
                return;
            }
            const resultDiv = document.getElementById('qaResult');
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = '<div class="loading"><div class="spinner"></div>正在思考...</div>';
            try {
                const response = await fetch(`${API_BASE}/ask`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question })
                });
                const data = await response.json();
                resultDiv.textContent = data.answer || '未获取到回答';
            } catch (error) {
                resultDiv.textContent = '请求失败: ' + error.message;
            }
        }

        async function analyzeSimilarity() {
            const resultDiv = document.getElementById('similarityResult');
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = '<div class="loading"><div class="spinner"></div>正在分析...</div>';
            try {
                const response = await fetch(`${API_BASE}/analyze_similarity`, {
                    method: 'POST'
                });
                const data = await response.json();
                resultDiv.textContent = data.result || '分析失败';
            } catch (error) {
                resultDiv.textContent = '请求失败: ' + error.message;
            }
        }

        async function recommendResearch() {
            const resultDiv = document.getElementById('recommendResult');
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = '<div class="loading"><div class="spinner"></div>正在生成推荐...</div>';
            try {
                const response = await fetch(`${API_BASE}/recommend`, {
                    method: 'POST'
                });
                const data = await response.json();
                resultDiv.textContent = data.result || '推荐失败';
            } catch (error) {
                resultDiv.textContent = '请求失败: ' + error.message;
            }
        }

        async function loadWebContents() {
            try {
                const response = await fetch(`${API_BASE}/web/contents`);
                const data = await response.json();
                const list = document.getElementById('webContentsList');
                if (list) {
                    list.innerHTML = '';
                    if (data.contents.length === 0) {
                        list.innerHTML = '<li>暂无网页内容</li>';
                    } else {
                        data.contents.forEach(content => {
                            const li = document.createElement('li');
                            li.textContent = content;
                            list.appendChild(li);
                        });
                    }
                }
            } catch (error) {
                console.error('加载网页内容列表失败:', error);
            }
        }

        async function fetchAndSummarize() {
            const url = document.getElementById('webUrl').value.trim();
            const focus = document.getElementById('webFocus').value.trim() || '复习总结';
            
            if (!url) {
                alert('请输入URL');
                return;
            }

            const resultDiv = document.getElementById('webResult');
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = '<div class="loading"><div class="spinner"></div>正在抓取网页并生成总结...</div>';

            try {
                const response = await fetch(`${API_BASE}/web/summarize`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url, focus })
                });
                
                const data = await response.json();
                if (data.error) {
                    resultDiv.textContent = '错误: ' + data.error;
                } else {
                    resultDiv.textContent = data.summary || '总结生成失败';
                    // 更新网页内容列表
                    loadWebContents();
                    checkStatus();
                }
            } catch (error) {
                resultDiv.textContent = '请求失败: ' + error.message;
            }
        }

        checkStatus();
        setInterval(checkStatus, 30000);
    </script>
</body>
</html>
'''

    @app.route('/api/ask', methods=['POST'])
    def ask():
        data = request.json
        question = data.get('question', '')
        if not question:
            return jsonify({'error': '问题不能为空'}), 400
        answer = assistant.ask(question)
        return jsonify({'answer': answer})

    @app.route('/api/analyze_similarity', methods=['POST'])
    def analyze_similarity():
        result = assistant.analyze_similarity()
        return jsonify({'result': result})

    @app.route('/api/recommend', methods=['POST'])
    def recommend():
        result = assistant.recommend_research()
        return jsonify({'result': result})

    @app.route('/api/documents', methods=['GET'])
    def get_documents():
        documents = assistant.get_document_list()
        return jsonify({'documents': documents})

    @app.route('/api/status', methods=['GET'])
    def status():
        return jsonify({
            'indexed': assistant.is_indexed,
            'document_count': len(assistant.documents_text),
            'web_content_count': len(assistant.web_contents)
        })
    
    @app.route('/api/web/fetch', methods=['POST'])
    def fetch_web():
        """抓取网页接口"""
        data = request.json
        url = data.get('url', '')
        if not url:
            return jsonify({'error': 'URL不能为空'}), 400
        
        try:
            result = assistant.fetch_web_content(url)
            if result:
                return jsonify({
                    'success': True,
                    'title': result['title'],
                    'content_length': result['length'],
                    'message': '网页内容已抓取'
                })
            else:
                return jsonify({'error': '网页抓取失败'}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/web/summarize', methods=['POST'])
    def summarize_web():
        """总结网页接口"""
        data = request.json
        url = data.get('url', '')
        focus = data.get('focus', '复习总结')
        
        if not url:
            return jsonify({'error': 'URL不能为空'}), 400
        
        try:
            summary = assistant.summarize_web_content(url, focus)
            return jsonify({'summary': summary})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/web/contents', methods=['GET'])
    def get_web_contents():
        """获取已抓取的网页列表"""
        contents = assistant.get_web_contents_list()
        return jsonify({'contents': contents})

    return app