#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MindSpider 话题提取工具
功能：每日自动抓取 12 个新闻源热搜，筛选化工外贸相关话题
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from datetime import date

# 添加项目路径
PROJECT_ROOT = Path("/root/.hermes/projects/trade-risk-alert")
BETTAFISH_DIR = PROJECT_ROOT / "BettaFish"
MINDSPIDER_DIR = BETTAFISH_DIR / "MindSpider"

# 确保路径正确
sys.path.insert(0, str(MINDSPIDER_DIR / "BroadTopicExtraction"))

class MindSpiderTopicExtractor:
    """MindSpider 话题提取器"""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.data_dir = self.project_root / "data"
        self.data_dir.mkdir(exist_ok=True)
        
    async def extract_topics(self, sources=None):
        """
        提取热点话题
        
        Args:
            sources: 指定新闻源列表，None 表示全部
            
        Returns:
            dict: 提取结果
        """
        # 导入 NewsCollector
        try:
            from get_today_news import NewsCollector
        except ImportError as e:
            print(f"❌ 导入 NewsCollector 失败：{e}")
            print("💡 提示：请先安装 BettaFish 依赖")
            return {"success": False, "error": str(e)}
        
        # 默认新闻源
        if sources is None:
            sources = [
                "weibo", "zhihu", "bilibili-hot-search", "toutiao",
                "douyin", "github-trending-today", "coolapk", "tieba",
                "wallstreetcn", "thepaper", "cls-hot", "xueqiu"
            ]
        
        print(f"📡 开始提取话题，目标源：{len(sources)} 个")
        
        async with NewsCollector() as collector:
            result = await collector.collect_and_save_news(sources=sources)
        
        # 保存结果
        output_file = self.data_dir / f"mindspider_topics_{date.today()}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 话题提取完成，保存至：{output_file}")
        print(f"📊 成功源：{result['successful_sources']}/{result['total_sources']}")
        print(f"📰 总话题数：{result['total_news']}")
        
        return result
    
    def filter_relevant_topics(self, topics, keywords=None):
        """
        筛选与化工外贸相关的话题
        
        Args:
            topics: 话题列表
            keywords: 关键词列表
            
        Returns:
            list: 筛选后的话题
        """
        if keywords is None:
            keywords = [
                "化工", "外贸", "贸易", "关税", "原油", "大宗商品",
                "汇率", "能源", "航运", "海运", "出口", "进口",
                "制裁", "政策", "供应链", "芯片", "半导体"
            ]
        
        relevant_topics = []
        for topic in topics:
            title = topic.get('title', '')
            # 检查是否包含关键词
            if any(kw in title for kw in keywords):
                relevant_topics.append(topic)
        
        print(f"🎯 筛选出 {len(relevant_topics)} 个相关话题")
        return relevant_topics


async def main():
    """主函数"""
    extractor = MindSpiderTopicExtractor()
    
    print("🚀 启动 MindSpider 话题提取...")
    print("=" * 50)
    
    # 提取话题
    result = await extractor.extract_topics()
    
    if result.get('success'):
        # 筛选相关话题
        relevant = extractor.filter_relevant_topics(result.get('news_list', []))
        
        # 保存筛选结果
        output_file = PROJECT_ROOT / "data" / f"mindspider_relevant_{date.today()}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(relevant, f, ensure_ascii=False, indent=2)
        
        print(f"💾 相关话题保存至：{output_file}")
        
        # 打印前 5 个相关话题
        print("\n📋 前 5 个相关话题：")
        for i, topic in enumerate(relevant[:5], 1):
            print(f"  {i}. {topic.get('title', 'N/A')} (来源：{topic.get('source', 'N/A')})")
    else:
        print(f"❌ 话题提取失败：{result.get('error')}")
        print("💡 请先安装依赖：cd BettaFish/MindSpider && uv pip install -r requirements.txt")


if __name__ == "__main__":
    asyncio.run(main())
