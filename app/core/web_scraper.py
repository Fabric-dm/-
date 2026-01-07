"""
网页内容抓取模块
支持从URL抓取网页内容，特别优化了对DeepSeek等AI对话页面的支持
"""
import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict
import re
from urllib.parse import urlparse


class WebScraper:
    """网页内容抓取器"""
    
    def __init__(self, timeout: int = 30):
        """
        初始化网页抓取器
        """
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def fetch_url(self, url: str) -> Optional[Dict[str, str]]:
        """
        抓取网页内容
        返回包含标题和内容的字典
        """
        try:
            # 验证URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            print(f"正在访问: {url}")
            
            # 发送请求
            response = requests.get(url, headers=self.headers, timeout=self.timeout, allow_redirects=True)
            response.raise_for_status()
            response.encoding = response.apparent_encoding or 'utf-8'
            
            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取标题
            title = self._extract_title(soup, url)
            
            # 提取主要内容
            content = self._extract_content(soup, url)
            
            if not content or len(content.strip()) < 50:
                return None
            
            return {
                'url': url,
                'title': title,
                'content': content.strip(),
                'length': len(content)
            }
            
        except requests.exceptions.Timeout:
            print(f"请求超时: {url}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            return None
        except Exception as e:
            print(f"抓取网页时出错: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup, url: str) -> str:
        """提取网页标题"""
        # 尝试多种方式提取标题
        title = None
        
        # 1. 从title标签
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)
        
        # 2. 从og:title
        if not title:
            og_title = soup.find('meta', property='og:title')
            if og_title:
                title = og_title.get('content', '').strip()
        
        # 3. 从h1标签
        if not title:
            h1_tag = soup.find('h1')
            if h1_tag:
                title = h1_tag.get_text(strip=True)
        
        # 如果没有找到标题，使用URL
        if not title:
            parsed = urlparse(url)
            title = parsed.netloc or url
        
        return title[:200]  # 限制标题长度
    
    def _extract_content(self, soup: BeautifulSoup, url: str) -> str:
        """提取网页主要内容"""
        
        # 特殊处理：DeepSeek对话页面
        if 'deepseek.com' in url or 'chat.deepseek.com' in url:
            return self._extract_deepseek_content(soup)
        
        # 移除script和style标签
        for script in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            script.decompose()
        
        # 尝试多种内容提取策略
        
        # 策略1: 查找article标签
        article = soup.find('article')
        if article:
            content = self._clean_text(article.get_text())
            if len(content) > 100:
                return content
        
        # 策略2: 查找main标签
        main = soup.find('main')
        if main:
            content = self._clean_text(main.get_text())
            if len(content) > 100:
                return content
        
        # 策略3: 查找特定class的内容区域
        content_selectors = [
            '.content', '.post-content', '.article-content',
            '.main-content', '#content', '#main-content',
            '.entry-content', '.post-body', '.article-body'
        ]
        
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                content = self._clean_text(element.get_text())
                if len(content) > 100:
                    return content
        
        # 策略4: 查找所有p标签并组合
        paragraphs = soup.find_all('p')
        if paragraphs:
            texts = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
            content = '\n\n'.join(texts)
            if len(content) > 100:
                return self._clean_text(content)
        
        # 策略5: 提取body中的所有文本
        body = soup.find('body')
        if body:
            content = self._clean_text(body.get_text())
            if len(content) > 100:
                return content
        
        return ""
    
    def _extract_deepseek_content(self, soup: BeautifulSoup) -> str:
        """专门提取DeepSeek对话页面的内容"""
        content_parts = []
        
        # 尝试查找对话容器
        # DeepSeek通常使用特定的class或data属性
        conversation_selectors = [
            '[class*="message"]',
            '[class*="chat"]',
            '[class*="conversation"]',
            '[data-testid*="message"]',
            '.markdown-body',  # 可能使用markdown渲染
        ]
        
        for selector in conversation_selectors:
            elements = soup.select(selector)
            if elements:
                for elem in elements:
                    text = elem.get_text(strip=True)
                    if text and len(text) > 20:
                        content_parts.append(text)
        
        # 如果找到对话内容，组合起来
        if content_parts:
            return '\n\n'.join(content_parts)
        
        # 备选方案：提取所有可见文本，过滤掉导航等
        for script in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            script.decompose()
        
        # 查找所有包含文本的div
        text_divs = soup.find_all('div', string=re.compile(r'.{50,}'))
        if text_divs:
            texts = [div.get_text(strip=True) for div in text_divs if len(div.get_text(strip=True)) > 50]
            return '\n\n'.join(texts[:20])  # 限制数量
        
        # 最后备选：提取body文本
        body = soup.find('body')
        if body:
            return self._clean_text(body.get_text())
        
        return ""
    
    def _clean_text(self, text: str) -> str:
        """清理文本：移除多余的空白字符"""
        # 移除多余的空行
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        # 移除行首行尾空白
        lines = [line.strip() for line in text.split('\n')]
        # 移除空行
        lines = [line for line in lines if line]
        return '\n\n'.join(lines)
