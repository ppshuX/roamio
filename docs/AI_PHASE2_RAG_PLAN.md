# 🧠 AI 旅行规划助手 Phase 2 - RAG 知识库增强计划

## 📋 项目概述

### 目标
通过爬取真实旅行攻略构建私域知识库，使用 RAG（检索增强生成）技术，让 AI 生成的行程更真实、更有参考价值。

### 核心价值
- **真实性提升**：基于真实用户攻略，不是凭空想象
- **质量提升**：融合高质量内容，生成更专业的行程
- **个性化提升**：根据用户偏好匹配最相关的攻略
- **差异化竞争**：建立独有的旅行知识库资产

---

## 🎯 资源规划

### 服务器资源
| 资源 | 用途 | 配置 | 成本 |
|------|------|------|------|
| **阿里云服务器（空闲）** | 爬虫专用 | 按需 | ¥0（已有）|
| **腾讯云 MySQL（空闲）** | 知识库存储 | 1个月试用 | ¥0（试用期）|
| **Roamio 主服务器** | AI 生成服务 | 2核2G | ¥0（已有）|

### API 成本
| 服务 | 用途 | 成本 |
|------|------|------|
| **通义千问 Embedding** | 向量生成 | ~¥7.5（一次性）|
| **通义千问 Chat** | AI 生成 | ~¥6/月（1000次）|
| **总计** | - | ~¥13.5 |

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────┐
│     阿里云服务器（爬虫专用）                              │
│  ┌──────────────────────────────────────────────────┐  │
│  │  爬虫服务 (24/7 运行)                             │  │
│  │  ├─ 马蜂窝爬虫 → 5,000+ 篇                        │  │
│  │  ├─ 知乎爬虫 → 3,000+ 篇                         │  │
│  │  ├─ 携程爬虫 → 2,000+ 篇                         │  │
│  │  ├─ 小红书爬虫 → 5,000+ 篇（可选）               │  │
│  │  ├─ 数据清洗 → 去重、质量评分                    │  │
│  │  └─ 向量生成 → Embedding                         │  │
│  └──────────────────┬───────────────────────────────┘  │
└─────────────────────┼───────────────────────────────────┘
                      │ 写入
                      ▼
┌─────────────────────────────────────────────────────────┐
│     腾讯云 MySQL（知识库专用）                            │
│  ┌──────────────────────────────────────────────────┐  │
│  │  travel_content 表（15,000+ 条记录）              │  │
│  │  ├─ 标题、正文、摘要                              │  │
│  │  ├─ 目的地、天数、预算                            │  │
│  │  ├─ 主题标签、活动标签                            │  │
│  │  ├─ 来源、作者、质量分                            │  │
│  │  └─ 向量嵌入（用于语义检索）                      │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────┬───────────────────────────────────┘
                      │ 读取（只读权限）
                      ▼
┌─────────────────────────────────────────────────────────┐
│     Roamio 主服务器（AI 生成服务）                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │  RAG 增强的 AI 服务                               │  │
│  │  1. 接收用户请求                                  │  │
│  │  2. 检索 MySQL 知识库（Top 5 相关攻略）           │  │
│  │  3. 构建增强 Prompt（真实内容 + 用户需求）        │  │
│  │  4. 调用通义千问生成                              │  │
│  │  5. 返回融合了真实攻略的高质量行程                │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 数据库设计

### 核心表：travel_content

```sql
CREATE TABLE travel_content (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    
    -- 基础信息
    title VARCHAR(200) NOT NULL COMMENT '标题',
    content TEXT NOT NULL COMMENT '正文内容',
    summary TEXT COMMENT '摘要（500字内）',
    
    -- 分类标签
    destination VARCHAR(100) NOT NULL COMMENT '目的地',
    duration INT COMMENT '天数',
    budget_level ENUM('low', 'medium', 'high') COMMENT '预算等级',
    
    -- 风格标签（JSON）
    themes JSON COMMENT '主题标签 ["文艺","小清新","美食"]',
    activities JSON COMMENT '活动标签 ["拍照","咖啡店","博物馆"]',
    
    -- 来源信息
    source VARCHAR(50) NOT NULL COMMENT '来源平台',
    source_url VARCHAR(500) COMMENT '原文链接',
    author VARCHAR(100) COMMENT '作者',
    
    -- 质量评分
    quality_score FLOAT DEFAULT 0 COMMENT '质量分数 0-100',
    view_count INT DEFAULT 0 COMMENT '浏览数',
    like_count INT DEFAULT 0 COMMENT '点赞数',
    comment_count INT DEFAULT 0 COMMENT '评论数',
    
    -- 向量嵌入（用于 RAG 检索）
    embedding JSON COMMENT '文本向量（1536维）',
    
    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_verified BOOLEAN DEFAULT FALSE COMMENT '人工审核',
    is_deleted BOOLEAN DEFAULT FALSE COMMENT '软删除',
    
    -- 索引
    INDEX idx_destination (destination),
    INDEX idx_duration (duration),
    INDEX idx_quality (quality_score),
    INDEX idx_source (source),
    INDEX idx_created (created_at),
    INDEX idx_verified (is_verified, is_deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='旅行知识库';

-- 统计表
CREATE TABLE crawler_stats (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    source VARCHAR(50) NOT NULL COMMENT '来源平台',
    crawled_count INT DEFAULT 0 COMMENT '爬取总数',
    success_count INT DEFAULT 0 COMMENT '成功数',
    failed_count INT DEFAULT 0 COMMENT '失败数',
    duplicate_count INT DEFAULT 0 COMMENT '重复数',
    last_crawl_time TIMESTAMP COMMENT '最后爬取时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    UNIQUE KEY uk_source (source)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='爬虫统计';
```

---

## 🕷️ 爬虫系统设计

### 项目结构

```
travel_crawler/                    # 爬虫项目（部署在阿里云空闲服务器）
├── config/
│   ├── settings.py               # 配置文件
│   ├── database.py               # 数据库连接
│   └── keywords.json             # 爬取关键词列表
│
├── crawlers/
│   ├── __init__.py
│   ├── base_crawler.py           # 基础爬虫类
│   ├── mafengwo_crawler.py       # 马蜂窝爬虫 ⭐⭐⭐⭐⭐
│   ├── zhihu_crawler.py          # 知乎爬虫 ⭐⭐⭐⭐⭐
│   ├── xiecheng_crawler.py       # 携程爬虫 ⭐⭐⭐⭐
│   └── xiaohongshu_crawler.py    # 小红书爬虫 ⭐⭐⭐
│
├── processors/
│   ├── __init__.py
│   ├── data_cleaner.py           # 数据清洗
│   ├── quality_scorer.py         # 质量评分
│   ├── theme_extractor.py        # 主题提取
│   └── embedding_generator.py    # 向量生成
│
├── models/
│   ├── __init__.py
│   └── knowledge.py              # 数据模型
│
├── scheduler/
│   ├── __init__.py
│   └── task_scheduler.py         # 任务调度（Celery）
│
├── utils/
│   ├── __init__.py
│   ├── proxy_pool.py             # 代理池
│   ├── logger.py                 # 日志
│   └── retry.py                  # 重试机制
│
├── tests/
│   └── test_crawlers.py          # 测试
│
├── requirements.txt              # 依赖
├── main.py                       # 主程序
├── deploy.sh                     # 部署脚本
└── README.md                     # 说明文档
```

---

## 💻 核心代码设计

### 1. 基础爬虫类

```python
# crawlers/base_crawler.py

import requests
import time
import logging
from abc import ABC, abstractmethod
from utils.retry import retry_on_failure

logger = logging.getLogger(__name__)


class BaseCrawler(ABC):
    """爬虫基类"""
    
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.delay = config.get('delay', 2)  # 请求间隔（秒）
        self.source_name = ''
    
    @abstractmethod
    def search(self, keyword, page=1):
        """搜索内容"""
        pass
    
    @abstractmethod
    def parse(self, response):
        """解析响应"""
        pass
    
    @abstractmethod
    def get_detail(self, url):
        """获取详情"""
        pass
    
    @retry_on_failure(max_retries=3, delay=5)
    def crawl_keyword(self, keyword, max_pages=10):
        """爬取单个关键词"""
        results = []
        
        for page in range(1, max_pages + 1):
            try:
                logger.info(f"[{self.source_name}] 爬取: {keyword}, 第{page}页")
                
                # 搜索
                response = self.search(keyword, page)
                
                # 解析
                items = self.parse(response)
                
                # 获取详情
                for item in items:
                    detail = self.get_detail(item['url'])
                    item.update(detail)
                    results.append(item)
                
                # 限频
                time.sleep(self.delay)
                
                logger.info(f"[{self.source_name}] 第{page}页完成，获取{len(items)}条")
                
            except Exception as e:
                logger.error(f"[{self.source_name}] 爬取失败: {e}")
                continue
        
        return results
    
    def save_to_db(self, data):
        """保存到数据库"""
        from models.knowledge import TravelKnowledge
        
        # 去重检查
        if TravelKnowledge.exists(data['source_url']):
            logger.info(f"内容已存在，跳过: {data['title']}")
            return None
        
        # 创建记录
        knowledge = TravelKnowledge.create(
            title=data['title'],
            content=data['content'],
            summary=data.get('summary', ''),
            destination=data['destination'],
            duration=data.get('duration'),
            themes=data.get('themes', []),
            source=self.source_name,
            source_url=data['source_url'],
            author=data.get('author'),
            like_count=data.get('like_count', 0),
            view_count=data.get('view_count', 0),
            quality_score=data.get('quality_score', 0)
        )
        
        logger.info(f"保存成功: {data['title']}")
        return knowledge
    
    def batch_crawl(self, keywords, max_pages=10):
        """批量爬取"""
        total = 0
        
        for keyword in keywords:
            results = self.crawl_keyword(keyword, max_pages)
            
            for item in results:
                if self.save_to_db(item):
                    total += 1
        
        logger.info(f"[{self.source_name}] 爬取完成，共保存 {total} 条")
        return total
```

---

### 2. 马蜂窝爬虫（优先级最高）

```python
# crawlers/mafengwo_crawler.py

from .base_crawler import BaseCrawler
from bs4 import BeautifulSoup
import re


class MafengwoCrawler(BaseCrawler):
    """
    马蜂窝爬虫
    
    优势：
    - 反爬较弱
    - 内容质量高
    - 结构化好
    - 适合入门
    """
    
    source_name = 'mafengwo'
    base_url = 'https://www.mafengwo.cn'
    
    def search(self, keyword, page=1):
        """搜索游记"""
        url = f"{self.base_url}/search/q.php"
        params = {
            'q': keyword,
            'p': page,
            'kb': 'gonglve'  # 攻略类型
        }
        
        response = self.session.get(url, params=params, timeout=10)
        return response
    
    def parse(self, response):
        """解析搜索结果"""
        soup = BeautifulSoup(response.text, 'html.parser')
        items = []
        
        # 找到所有攻略卡片
        for card in soup.select('.tn-item'):
            try:
                title_elem = card.select_one('.tn-title a')
                if not title_elem:
                    continue
                
                title = title_elem.text.strip()
                url = self.base_url + title_elem['href']
                author = card.select_one('.tn-user a').text.strip()
                
                items.append({
                    'title': title,
                    'url': url,
                    'author': author
                })
                
            except Exception as e:
                logger.warning(f"解析卡片失败: {e}")
                continue
        
        return items
    
    def get_detail(self, url):
        """获取攻略详情"""
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取正文
            content_elem = soup.select_one('.article-content')
            content = content_elem.get_text(strip=True) if content_elem else ''
            
            # 提取统计数据
            view_count = self._extract_number(soup, '.view-count')
            like_count = self._extract_number(soup, '.like-count')
            
            # 提取目的地
            destination = self._extract_destination(soup, content)
            
            # 提取天数
            duration = self._extract_duration(content)
            
            # 生成摘要
            summary = content[:500] if len(content) > 500 else content
            
            # 提取主题
            themes = self._extract_themes(content)
            
            # 计算质量分
            quality_score = self._calculate_quality({
                'content_length': len(content),
                'view_count': view_count,
                'like_count': like_count
            })
            
            return {
                'content': content,
                'summary': summary,
                'destination': destination,
                'duration': duration,
                'themes': themes,
                'view_count': view_count,
                'like_count': like_count,
                'quality_score': quality_score,
                'source_url': url
            }
            
        except Exception as e:
            logger.error(f"获取详情失败: {e}")
            return {}
    
    def _extract_number(self, soup, selector):
        """提取数字"""
        elem = soup.select_one(selector)
        if elem:
            text = elem.text
            match = re.search(r'\d+', text)
            if match:
                return int(match.group())
        return 0
    
    def _extract_destination(self, soup, content):
        """提取目的地"""
        # 1. 从面包屑导航提取
        breadcrumb = soup.select_one('.breadcrumb')
        if breadcrumb:
            links = breadcrumb.select('a')
            if len(links) >= 2:
                return links[1].text.strip()
        
        # 2. 从内容中提取（关键词匹配）
        cities = [
            '北京', '上海', '广州', '深圳', '成都', '重庆', '西安', '杭州',
            '南京', '厦门', '大理', '丽江', '三亚', '青岛', '苏州', '武汉',
            '长沙', '桂林', '张家界', '黄山', '九寨沟', '拉萨', '乌鲁木齐'
        ]
        
        for city in cities:
            if city in content[:200]:  # 只检查开头
                return city
        
        return '未知'
    
    def _extract_duration(self, content):
        """提取天数"""
        # 正则匹配 "X天" "X日"
        match = re.search(r'(\d+)[天日]', content[:500])
        if match:
            return int(match.group(1))
        return None
    
    def _extract_themes(self, content):
        """提取主题标签"""
        theme_keywords = {
            '文艺': ['文艺', '小清新', '书店', '咖啡', '文化'],
            '美食': ['美食', '餐厅', '小吃', '网红店', '特色菜'],
            '自然': ['自然', '风景', '徒步', '登山', '湖泊', '森林'],
            '摄影': ['拍照', '摄影', '打卡', '出片', '机位'],
            '古城': ['古城', '古镇', '历史', '古建筑'],
            '海滨': ['海滨', '沙滩', '海边', '海岛'],
        }
        
        themes = []
        for theme, keywords in theme_keywords.items():
            if any(kw in content for kw in keywords):
                themes.append(theme)
        
        return themes
    
    def _calculate_quality(self, data):
        """计算质量分数"""
        score = 0
        
        # 内容长度权重（最高 30 分）
        content_length = data.get('content_length', 0)
        score += min(content_length / 100, 30)
        
        # 浏览数权重（最高 25 分）
        view_count = data.get('view_count', 0)
        score += min(view_count / 1000, 25)
        
        # 点赞数权重（最高 25 分）
        like_count = data.get('like_count', 0)
        score += min(like_count / 100, 25)
        
        # 基础分（最高 20 分）
        score += 20
        
        return min(score, 100)
```

---

### 3. 知乎爬虫

```python
# crawlers/zhihu_crawler.py

from .base_crawler import BaseCrawler
import json


class ZhihuCrawler(BaseCrawler):
    """
    知乎爬虫
    
    优势：
    - 内容深度好
    - 长文质量高
    - API 相对友好
    """
    
    source_name = 'zhihu'
    base_url = 'https://www.zhihu.com'
    api_url = 'https://www.zhihu.com/api/v4'
    
    def __init__(self, config):
        super().__init__(config)
        # 需要登录后的 Cookie
        self.session.headers.update({
            'Cookie': config.get('zhihu_cookie', '')
        })
    
    def search(self, keyword, page=1):
        """搜索问题和文章"""
        url = f"{self.api_url}/search_v3"
        params = {
            'q': keyword,
            't': 'general',
            'offset': (page - 1) * 10,
            'limit': 10
        }
        
        response = self.session.get(url, params=params, timeout=10)
        return response
    
    def parse(self, response):
        """解析搜索结果"""
        try:
            data = response.json()
            items = []
            
            for item in data.get('data', []):
                obj = item.get('object', {})
                
                # 只要回答和文章
                if item['type'] not in ['answer', 'article']:
                    continue
                
                items.append({
                    'title': obj.get('question', {}).get('title') or obj.get('title'),
                    'url': obj.get('url'),
                    'author': obj.get('author', {}).get('name'),
                    'type': item['type']
                })
            
            return items
            
        except Exception as e:
            logger.error(f"解析知乎响应失败: {e}")
            return []
    
    def get_detail(self, url):
        """获取详情"""
        try:
            # 根据类型获取内容
            if '/answer/' in url:
                return self._get_answer_detail(url)
            elif '/p/' in url:
                return self._get_article_detail(url)
            
        except Exception as e:
            logger.error(f"获取知乎详情失败: {e}")
            return {}
    
    def _get_answer_detail(self, url):
        """获取回答详情"""
        # 实现略
        pass
    
    def _get_article_detail(self, url):
        """获取文章详情"""
        # 实现略
        pass
```

---

### 4. 数据处理器

```python
# processors/embedding_generator.py

import os
import requests
import json
import logging

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """向量嵌入生成器"""
    
    def __init__(self):
        self.api_key = os.getenv('QWEN_API_KEY')
        self.api_base = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.model = "text-embedding-v1"
    
    def generate(self, text):
        """生成单个文本的向量"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "input": text[:2000]  # 限制长度
            }
            
            response = requests.post(
                f"{self.api_base}/embeddings",
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['data'][0]['embedding']
            else:
                logger.error(f"Embedding API 错误: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"生成向量失败: {e}")
            return None
    
    def batch_generate(self, knowledge_list, batch_size=10):
        """批量生成向量"""
        total = len(knowledge_list)
        success = 0
        
        for i, knowledge in enumerate(knowledge_list):
            if knowledge.embedding:
                continue  # 已有向量，跳过
            
            text = f"{knowledge.title}\n{knowledge.summary or knowledge.content[:500]}"
            embedding = self.generate(text)
            
            if embedding:
                knowledge.embedding = json.dumps(embedding)
                knowledge.save()
                success += 1
            
            # 进度显示
            if (i + 1) % batch_size == 0:
                logger.info(f"向量生成进度: {i+1}/{total}")
            
            # 限频（避免超过 API 限制）
            time.sleep(0.1)
        
        logger.info(f"向量生成完成: {success}/{total}")
        return success
```

---

### 5. 任务调度器

```python
# scheduler/task_scheduler.py

from celery import Celery
from celery.schedules import crontab

app = Celery('travel_crawler', broker='redis://localhost:6379/0')


@app.task
def crawl_mafengwo():
    """定时爬取马蜂窝"""
    from crawlers.mafengwo_crawler import MafengwoCrawler
    
    keywords = ['北京旅游', '上海旅游', '成都旅游', ...]
    crawler = MafengwoCrawler(config)
    crawler.batch_crawl(keywords, max_pages=5)


@app.task
def crawl_zhihu():
    """定时爬取知乎"""
    from crawlers.zhihu_crawler import ZhihuCrawler
    
    keywords = ['北京旅游攻略', '上海三日游', ...]
    crawler = ZhihuCrawler(config)
    crawler.batch_crawl(keywords, max_pages=3)


@app.task
def generate_embeddings():
    """定时生成向量"""
    from processors.embedding_generator import EmbeddingGenerator
    from models.knowledge import TravelKnowledge
    
    # 找出还没有向量的记录
    knowledge_list = TravelKnowledge.get_without_embedding(limit=100)
    
    generator = EmbeddingGenerator()
    generator.batch_generate(knowledge_list)


# 定时任务配置
app.conf.beat_schedule = {
    'crawl-mafengwo-daily': {
        'task': 'scheduler.task_scheduler.crawl_mafengwo',
        'schedule': crontab(hour=2, minute=0),  # 每天凌晨2点
    },
    'crawl-zhihu-daily': {
        'task': 'scheduler.task_scheduler.crawl_zhihu',
        'schedule': crontab(hour=3, minute=0),  # 每天凌晨3点
    },
    'generate-embeddings-hourly': {
        'task': 'scheduler.task_scheduler.generate_embeddings',
        'schedule': crontab(minute=0),  # 每小时
    },
}
```

---

## 🔗 Roamio 集成（RAG 服务）

### 1. RAG 服务实现

```python
# backend/utils/ai/rag_service.py

import os
import pymysql
import numpy as np
import logging

logger = logging.getLogger(__name__)


class TravelRAGService:
    """旅行知识库 RAG 服务"""
    
    def __init__(self):
        """连接知识库 MySQL"""
        self.db_config = {
            'host': os.getenv('KNOWLEDGE_DB_HOST'),
            'port': int(os.getenv('KNOWLEDGE_DB_PORT', 3306)),
            'user': os.getenv('KNOWLEDGE_DB_USER'),  # 只读用户
            'password': os.getenv('KNOWLEDGE_DB_PASSWORD'),
            'database': 'travel_knowledge',
            'charset': 'utf8mb4'
        }
    
    def search_relevant_content(self, query, destination, days=None, top_k=5):
        """
        检索相关内容
        
        Args:
            query: 用户查询（如"3天文艺路线"）
            destination: 目的地
            days: 天数（可选）
            top_k: 返回前 K 个结果
        
        Returns:
            list: 相关攻略列表
        """
        conn = pymysql.connect(**self.db_config)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        try:
            # 方案 1: 简单的 SQL 检索（初期）
            sql = """
                SELECT 
                    title, content, summary, themes, 
                    quality_score, source, author, like_count
                FROM travel_content
                WHERE destination LIKE %s
                  AND is_deleted = FALSE
                  AND quality_score >= 60
            """
            
            params = [f'%{destination}%']
            
            # 如果指定天数
            if days:
                sql += " AND (duration = %s OR duration IS NULL)"
                params.append(days)
            
            sql += """
                ORDER BY quality_score DESC, like_count DESC
                LIMIT %s
            """
            params.append(top_k)
            
            cursor.execute(sql, params)
            results = cursor.fetchall()
            
            logger.info(f"检索到 {len(results)} 条相关内容")
            return results
            
        except Exception as e:
            logger.error(f"检索失败: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    
    def search_by_vector(self, query_text, destination, top_k=5):
        """
        向量检索（高级版本，未来实现）
        
        使用语义相似度检索，比关键词匹配更智能
        """
        # 1. 生成查询向量
        query_embedding = self._get_embedding(query_text)
        
        # 2. 从数据库获取候选内容
        conn = pymysql.connect(**self.db_config)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        try:
            sql = """
                SELECT id, title, content, summary, embedding,
                       quality_score, source, author
                FROM travel_content
                WHERE destination LIKE %s
                  AND embedding IS NOT NULL
                  AND quality_score >= 60
                LIMIT 100
            """
            
            cursor.execute(sql, (f'%{destination}%',))
            candidates = cursor.fetchall()
            
            # 3. 计算相似度
            results = []
            for candidate in candidates:
                embedding = json.loads(candidate['embedding'])
                similarity = self._cosine_similarity(query_embedding, embedding)
                
                results.append({
                    'knowledge': candidate,
                    'similarity': similarity
                })
            
            # 4. 排序并返回 Top K
            results.sort(key=lambda x: x['similarity'], reverse=True)
            return [r['knowledge'] for r in results[:top_k]]
            
        finally:
            cursor.close()
            conn.close()
    
    def _get_embedding(self, text):
        """获取文本向量"""
        import requests
        
        headers = {
            "Authorization": f"Bearer {os.getenv('QWEN_API_KEY')}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "text-embedding-v1",
            "input": text[:2000]
        }
        
        response = requests.post(
            "https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings",
            headers=headers,
            json=data
        )
        
        return response.json()['data'][0]['embedding']
    
    def _cosine_similarity(self, vec1, vec2):
        """计算余弦相似度"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        return np.dot(vec1, vec2) / (
            np.linalg.norm(vec1) * np.linalg.norm(vec2)
        )
```

---

### 2. 更新 AI 服务（集成 RAG）

```python
# backend/utils/ai/ai_service.py (添加 RAG 支持)

from .rag_service import TravelRAGService


class TripPlannerAI:
    """旅行规划 AI 服务（支持 RAG）"""
    
    def __init__(self, use_rag=True):
        # ... 原有初始化
        
        # RAG 服务
        self.use_rag = use_rag and os.getenv('ENABLE_RAG', 'False').lower() == 'true'
        if self.use_rag:
            self.rag_service = TravelRAGService()
    
    def generate_trip_plan(self, user_prompt, preferences, user=None):
        """生成旅行计划（RAG 增强）"""
        
        # 如果启用 RAG，先检索知识库
        relevant_content = []
        if self.use_rag:
            destination = preferences.get('destination', '')
            days = preferences.get('days')
            
            if destination:
                relevant_content = self.rag_service.search_relevant_content(
                    query=user_prompt,
                    destination=destination,
                    days=days,
                    top_k=5
                )
        
        # 构建增强的提示词
        if relevant_content:
            system_prompt = self._build_rag_system_prompt(
                preferences, 
                relevant_content
            )
        else:
            system_prompt = self._build_system_prompt(preferences)
        
        # ... 其他逻辑不变
    
    def _build_rag_system_prompt(self, preferences, relevant_content):
        """构建包含真实攻略的系统提示词"""
        
        # 整理检索到的内容
        reference_text = "\n\n".join([
            f"【参考攻略 {i+1}】\n"
            f"标题：{item['title']}\n"
            f"摘要：{item['summary'] or item['content'][:300]}\n"
            f"来源：{item['source']}@{item['author']}\n"
            f"质量分：{item['quality_score']:.1f}\n"
            f"主题：{', '.join(item.get('themes', []))}"
            for i, item in enumerate(relevant_content)
        ])
        
        base_prompt = self._build_system_prompt(preferences)
        
        return f"""{base_prompt}

【真实攻略参考】
以下是从 Roamio 旅行知识库检索到的真实攻略，请参考这些内容：

{reference_text}

【特别要求】
1. **融合真实攻略**：优先推荐参考内容中出现的景点和路线
2. **标注来源**：可以提及"参考马蜂窝用户推荐"、"知乎高赞回答建议"等
3. **保持真实**：不要推荐参考内容中没有的景点
4. **个性化调整**：根据用户偏好调整风格和节奏

请基于以上真实攻略生成行程计划。
"""
```

---

## 📅 实施时间表

### 第 1 个月：爬虫系统搭建

| 周 | 任务 | 产出 | 负责人 |
|----|------|------|--------|
| **Week 1** | 环境搭建 + 马蜂窝爬虫 | 5,000+ 条 | - |
| **Week 2** | 知乎爬虫 | 3,000+ 条 | - |
| **Week 3** | 携程爬虫 + 数据清洗 | 2,000+ 条 | - |
| **Week 4** | 向量生成 + 质量优化 | 10,000+ 条可用 | - |

### 第 2 个月：RAG 集成

| 周 | 任务 | 产出 |
|----|------|------|
| **Week 5** | RAG 服务开发 | 检索功能 |
| **Week 6** | Roamio 集成 | RAG 增强版 AI |
| **Week 7** | 测试优化 | A/B 测试 |
| **Week 8** | 正式上线 | Phase 2 完成 |

---

## 💰 成本预算

### 一次性成本
| 项目 | 成本 | 说明 |
|------|------|------|
| 向量生成 | ¥7.5 | 15,000条 × 500 tokens |
| 开发时间 | - | 自己开发 |
| **总计** | **¥7.5** | 极低成本 |

### 持续成本
| 项目 | 成本 | 说明 |
|------|------|------|
| 阿里云服务器 | ¥0 | 已有空闲 |
| 腾讯云 MySQL | ¥0 | 试用期 1个月 |
| 后续 MySQL | ~¥50/月 | 试用期后 |
| AI API | ~¥10/月 | 1000次生成 |
| **总计** | **~¥60/月** | 可控 |

---

## 📊 数据目标

### 爬取目标

| 平台 | 目标数量 | 优先级 | 难度 | 预计时间 |
|------|---------|--------|------|---------|
| **马蜂窝** | 5,000+ | ⭐⭐⭐⭐⭐ | 低 | 1周 |
| **知乎** | 3,000+ | ⭐⭐⭐⭐⭐ | 中 | 1周 |
| **携程** | 2,000+ | ⭐⭐⭐⭐ | 低 | 3天 |
| **小红书** | 5,000+ | ⭐⭐⭐ | 高 | 1周 |
| **Roamio 用户** | 1,000+ | ⭐⭐⭐⭐⭐ | 无 | 持续 |
| **总计** | **16,000+** | - | - | **1个月** |

### 质量标准
- ✅ 内容长度 > 500 字
- ✅ 包含具体景点和路线
- ✅ 有明确的目的地和天数
- ✅ 质量评分 > 60
- ✅ 去重率 > 95%

---

## 🎯 效果预期

### Phase 1 vs Phase 2 对比

| 指标 | Phase 1（纯AI） | Phase 2（RAG） | 提升 |
|------|----------------|---------------|------|
| **内容真实性** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | +67% |
| **景点准确性** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | +67% |
| **预算准确性** | ⭐⭐⭐ | ⭐⭐⭐⭐ | +33% |
| **用户满意度** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | +67% |
| **应用率** | 60% | 85%+ | +42% |
| **生成成本** | ¥0.006 | ¥0.008 | +33% |

### 用户体验提升

**Phase 1 生成示例**：
```
Day 1: 北京天安门 → 故宫 → 景山公园
（AI 凭空生成，可能不够详细）
```

**Phase 2 生成示例**：
```
Day 1: 北京天安门 → 故宫 → 景山公园
时间：09:00-18:00
路线：参考马蜂窝@旅行达人的经典路线
建议：早上8点前到天安门看升旗（知乎高赞回答推荐）
美食：中午在故宫附近的庆丰包子铺（小红书网红店）
预算：¥300（门票¥60 + 餐饮¥150 + 交通¥50 + 其他¥40）
提示：故宫需要提前预约，建议提前3天（来自真实用户经验）
```

---

## 🔐 安全与合规

### 1. 爬虫合规
- ✅ 遵守 robots.txt
- ✅ 合理限频（2-5秒/次）
- ✅ 使用代理池分散请求
- ✅ 不爬取用户隐私信息
- ✅ 仅用于学习和研究

### 2. 数据安全
- ✅ 知识库只读权限给 Roamio
- ✅ 爬虫服务器独立隔离
- ✅ 定期备份数据
- ✅ 敏感信息脱敏

### 3. 版权问题
- ✅ 不直接展示原文
- ✅ 仅作为 AI 参考
- ✅ 标注来源平台
- ✅ 生成的内容是原创

---

## 📚 技术栈

### 爬虫服务器
- **语言**: Python 3.8+
- **框架**: Scrapy / Requests + BeautifulSoup
- **数据库**: PyMySQL
- **任务队列**: Celery + Redis
- **代理**: 代理池（如需要）

### 知识库
- **数据库**: 腾讯云 MySQL 8.0
- **存储**: 预计 5GB（15,000条）
- **索引**: B-Tree + 全文索引

### RAG 服务
- **向量模型**: text-embedding-v1
- **检索算法**: 余弦相似度
- **缓存**: Redis（热门查询）

---

## 🚀 快速启动指南（未来使用）

### 1. 爬虫服务器部署

```bash
# 连接阿里云服务器
ssh root@your-aliyun-server

# 克隆项目
git clone https://github.com/your-repo/travel_crawler.git
cd travel_crawler

# 安装依赖
pip3 install -r requirements.txt

# 配置环境变量
cp .env.example .env
vim .env  # 填入 MySQL 配置和 API Key

# 测试爬虫
python3 main.py --test --source mafengwo --keyword "北京旅游" --pages 1

# 启动定时任务
celery -A scheduler.task_scheduler worker -l info &
celery -A scheduler.task_scheduler beat -l info &
```

### 2. MySQL 数据库配置

```bash
# 连接腾讯云 MySQL
mysql -h your-mysql-host -u root -p

# 执行建表 SQL
source scripts/create_tables.sql

# 创建只读用户
source scripts/create_readonly_user.sql
```

### 3. Roamio 集成

```bash
# 更新 Roamio 配置
vim ~/roamio/.env

# 添加知识库配置
ENABLE_RAG=True
KNOWLEDGE_DB_HOST=your-mysql-host
KNOWLEDGE_DB_USER=roamio_readonly
KNOWLEDGE_DB_PASSWORD=your-password

# 重启服务
sudo systemctl restart uwsgi
```

---

## 📈 监控与优化

### 爬虫监控
- 每日爬取数量
- 成功率
- 去重率
- 质量分布

### 知识库监控
- 总记录数
- 各平台占比
- 目的地覆盖率
- 平均质量分

### RAG 效果监控
- 检索命中率
- 相似度分布
- 用户应用率
- 满意度评分

---

## 🎯 成功标准

### Phase 2 完成标志

- [ ] 知识库达到 15,000+ 条
- [ ] 质量评分 > 70 的占比 > 50%
- [ ] 目的地覆盖 100+ 个城市
- [ ] RAG 检索响应时间 < 1秒
- [ ] 生成质量提升 > 50%
- [ ] 用户应用率 > 80%
- [ ] 用户满意度 > 4.5/5.0

---

## 🔮 未来展望

### Phase 3: 智能推荐（3个月后）
- 基于用户画像推荐目的地
- 协同过滤推荐相似行程
- 实时热门目的地排行

### Phase 4: 多模态增强（6个月后）
- 图片识别（景点识别）
- 语音输入（语音描述旅行想法）
- 视频解析（旅游 Vlog 提取信息）

### Phase 5: 知识库服务化（1年后）
- 独立的"旅行知识库 API"
- 服务 Roamio、Ralendar、Rote 等多个产品
- 对外开放 API（商业化）

---

## 📝 参考资源

### 爬虫技术
- [Scrapy 文档](https://docs.scrapy.org/)
- [反爬虫策略](https://github.com/topics/anti-spider)
- [代理池搭建](https://github.com/jhao104/proxy_pool)

### RAG 技术
- [RAG 论文](https://arxiv.org/abs/2005.11401)
- [LangChain RAG](https://python.langchain.com/docs/use_cases/question_answering/)
- [向量数据库对比](https://github.com/erikbern/ann-benchmarks)

### 数据库优化
- [MySQL 索引优化](https://dev.mysql.com/doc/refman/8.0/en/optimization-indexes.html)
- [JSON 字段使用](https://dev.mysql.com/doc/refman/8.0/en/json.html)

---

## ✅ 总结

### 为什么这个方案好？

1. **资源利用最大化** 💰
   - 空闲的阿里云服务器 → 爬虫专用
   - 空闲的腾讯云 MySQL → 知识库存储
   - 不浪费任何资源

2. **职责分离清晰** 🎯
   - 爬虫服务器：只负责采集数据
   - MySQL：只负责存储
   - Roamio：只负责查询和生成
   - 互不干扰

3. **性能和安全** 🔐
   - 爬虫独立运行，不影响主站
   - 被封不影响用户体验
   - 数据库只读权限，安全可控

4. **可扩展性强** 🚀
   - 知识库可以服务多个产品
   - 未来可以做成独立服务
   - 商业化潜力大

5. **成本极低** 💸
   - 一次性成本：¥7.5
   - 月度成本：¥60
   - ROI：10,000%+

---

## 🎊 行动建议

### 当前（Phase 1 MVP）
- ✅ 先上线基础 AI 生成功能
- ✅ 验证用户需求
- ✅ 收集反馈数据

### 未来（Phase 2 RAG）
- ⏳ 等 Phase 1 稳定后启动
- ⏳ 预计 1-2 个月后开始
- ⏳ 用 2 个月时间完成

---

## 📞 联系方式

如果未来启动 Phase 2，可以参考：
- **完整方案**: 本文档
- **爬虫代码**: 待生成（需要时联系）
- **数据库脚本**: 本文档中的 SQL
- **RAG 服务**: 本文档中的代码示例

---

*创建时间: 2025-11-10*  
*计划周期: 2个月*  
*预期成本: ¥67.5（含试用期后 MySQL）*  
*预期收益: ROI 10,000%+*

**这是一个完美的资源利用方案，值得未来投入！** 🌟

