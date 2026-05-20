---
name: 微信公众号文章抓取
description: 通过搜狗微信搜索公开抓取微信公众号文章，绕过微信反爬验证，无需cookie
tags: [爬虫, 微信, 舆情, 数据采集]
---

# 微信公众号文章抓取 Skill

通过搜狗微信搜索公开接口抓取微信公众号文章，绕过微信官方验证码反爬，无需登录或cookie即可获取文章正文内容。

## 触发条件
- 需要获取微信公众号文章内容用于舆情分析
- 直接访问微信文章遇到验证码反爬
- 不需要点赞、阅读量等数据，只需要正文内容

## 使用步骤

1. **确认URL可访问**：通过浏览器打开文章链接，确认是公开可访问文章（非原创保护/私密）
2. **编写抓取脚本**：使用requests+BeautifulSoup抓取，通过搜狗搜索反代或直接解析微信页面
3. **提取正文内容**：清理HTML标签，提取纯文本正文
4. **保存数据**：保存到指定目录（一般为项目data/wechat_articles/），命名为日期_文章标题.json

## 完整代码示例

```python
import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

def fetch_wechat_article(url):
    """
    抓取微信公众号文章正文
    参数: url - 公众号文章链接
    返回: dict - {'title': 标题, 'content': 正文, 'author': 作者, 'publish_time': 发布时间}
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取标题
        title = soup.find('h1', id='activity-name')
        title = title.get_text(strip=True) if title else "未知标题"
        
        # 提取作者
        author = soup.find('span', id='js_author_name')
        author = author.get_text(strip=True) if author else "未知作者"
        
        # 提取发布时间
        publish_time = soup.find('em', id='post-date')
        publish_time = publish_time.get_text(strip=True) if publish_time else ""
        
        # 提取正文
        content_div = soup.find('div', id='js_content')
        if content_div:
            # 清理无用标签
            for tag in content_div.find_all(['style', 'script', 'div']):
                if 'class' in tag.attrs and ('rich_media_meta' in tag['class'] or 'copyright_area' in tag['class']):
                    tag.decompose()
            content = content_div.get_text(separator='\n', strip=True)
        else:
            content = ""
        
        return {
            "title": title,
            "content": content,
            "author": author,
            "publish_time": publish_time,
            "url": url,
            "crawl_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    except Exception as e:
        print(f"抓取失败: {e}")
        return None

def save_article(article_data, save_dir):
    """保存文章到JSON文件"""
    if not article_data:
        return False
    
    # 清理文件名中的特殊字符
    safe_title = re.sub(r'[\\/*?:"<>|]', '_', article_data['title'])[:50]
    filename = f"{datetime.now().strftime('%Y%m%d')}_{safe_title}.json"
    filepath = f"{save_dir}/{filename}"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(article_data, f, ensure_ascii=False, indent=2)
    
    print(f"文章已保存到: {filepath}")
    return filepath
```

## 坑点与注意事项

1. **反爬限制**：微信官方对频繁访问有风控，不要高频率抓取，一天抓取几篇没问题
2. **验证码**：如果遇到验证码，需要更换IP或者等待一段时间再试
3. **原创保护**：部分原创文章会隐藏内容，只能看到摘要，无法抓取全文
4. **搜狗反代方案**：直接抓取失败时，可以尝试通过搜狗微信搜索搜索标题找到文章链接再抓取

## 验证方法

运行脚本后检查：
1. 是否成功获取标题、作者、发布时间
2. 正文内容是否完整（检查开头和结尾）
3. JSON文件是否保存成功
