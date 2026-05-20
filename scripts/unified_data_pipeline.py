#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
「超越微舆」统一数据采集流水线 v2.0
整合多源数据，超越原始 BettaFish 能力
"""

import os, sys, json, sqlite3, asyncio, httpx, datetime
from pathlib import Path

PROJECT_ROOT = Path("/root/.hermes/projects/trade-risk-alert")
DATA_DIR = PROJECT_ROOT / "data"
TREND_RADAR_DIR = Path("/root/TrendRadar/output/news")
BETTAFISH_DIR = PROJECT_ROOT / "BettaFish" / "MindSpider" / "BroadTopicExtraction"
OUTPUT_DIR = DATA_DIR / "unified"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

today = datetime.date.today()
date_str = today.strftime("%Y-%m-%d")

# ============= 超越微舆的增强关键词 =============
# 比原始 BettaFish 更细致的化工外贸关键词体系
TRADE_KEYWORDS_V2 = {
    "core_trade": ['外贸', '出口', '进口', '国际贸易', '跨境', '进出口', '贸易逆差', '贸易顺差'],
    "policy": ['关税', '反倾销', '反补贴', '制裁', '禁运', '出口管制', '贸易壁垒', '配额', '自由贸易', 'RCEP', 'CPTPP'],
    "chemical": ['化工', '化工品', '石化', '塑料', '橡胶', '化纤', '聚丙烯', '聚乙烯', '乙二醇', '苯乙烯',
                 '甲醇', 'PTA', 'PVC', '烧碱', '纯碱', 'MDI', 'TDI', '钛白粉', '燃料油', '沥青', '硫磺', '尿素'],
    "energy": ['原油', '石油', '天然气', '成品油', 'WTI', '布伦特', 'OPEC', '能源', '炼化'],
    "logistics": ['航运', '海运', '港口', '集装箱', '货代', '运价', 'BDI', '苏伊士', '巴拿马'],
    "macro": ['人民币汇率', '美元', '美联储', '加息', '降息', '通胀', 'PMI', 'GDP'],
    "geopolitics": ['中美', '供应链', '产业链', '脱钩', '贸易战', '红海', '印太', '一带一路'],
    "emerging_markets": ['巴西', '南美', '拉丁美洲', '阿根廷', '智利', '秘鲁', '哥伦比亚',
                         '非洲', '尼日利亚', '南非', '埃及', '肯尼亚', '摩洛哥', '加纳',
                         '坦桑尼亚', '阿尔及利亚', '中非贸易', '中巴贸易', '中非合作论坛',
                         '西芒杜', '卡莫阿']
}

def get_all_keywords():
    all_kw = set()
    for cat, words in TRADE_KEYWORDS_V2.items():
        for w in words:
            all_kw.add(w)
    return list(all_kw)

# ============= 数据源 1: TrendRadar（最高质量新闻） =============
def collect_from_trendradar():
    """从 TrendRadar 同步化工外贸新闻"""
    db_path = TREND_RADAR_DIR / f"{date_str}.db"
    if not db_path.exists():
        print(f"  ✗ TrendRadar: {date_str}.db 不存在")
        return []
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, title, url, platform_id, rank FROM news_items")
        rows = cursor.fetchall()
    except:
        cursor.execute("SELECT id, title, url, platform_id, rank FROM news_items")
        rows = cursor.fetchall()
    
    keywords = get_all_keywords()
    synced = []
    for row in rows:
        news_id, title, url, platform, rank = (row + (None, None, None, None))[:5]
        if any(kw in (title or '') for kw in keywords):
            item = {
                "id": news_id, "title": title, "url": url or "",
                "source": f"TrendRadar/{platform or 'unknown'}",
                "category": "trendradar", "date": date_str,
                "matched_keywords": [kw for kw in keywords if kw in (title or '')]
            }
            synced.append(item)
    
    conn.close()
    print(f"  ✓ TrendRadar: {len(rows)} 条 → {len(synced)} 条外贸相关")
    return synced

# ============= 数据源 2: BettaFish MindSpider（社交媒体舆情） =============
async def collect_from_bettafish():
    """从 BettaFish 风格 API 获取社交媒体舆情（直接 HTTP 调用，更可靠）"""
    BASE_URL = "https://newsnow.busiyi.world"
    
    sources_map = {
        'cls-hot': '财联社', 'wallstreetcn': '华尔街见闻', 'thepaper': '澎湃新闻',
        'xueqiu': '雪球热榜', 'weibo': '微博热搜', 'zhihu': '知乎热榜'
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }
    
    all_news = []
    async with httpx.AsyncClient(timeout=15) as client:
        for src_id, src_name in sources_map.items():
            try:
                url = f"{BASE_URL}/api/s?id={src_id}&latest"
                resp = await client.get(url, headers=headers)
                data = resp.json()
                items = data.get('items', [])
                for i, item in enumerate(items):
                    all_news.append({
                        "title": item.get('title', ''), "url": item.get('url', ''),
                        "source": f"BettaFish/{src_id}", "category": "bettafish", 
                        "date": date_str, "rank": item.get('rank', i + 1)
                    })
                print(f"  ✓ BettaFish/{src_name}: {len(items)} 条")
            except Exception as e:
                print(f"  ⚠ BettaFish/{src_name}: {str(e)[:60]}")
    
    # 用增强关键词再次筛选
    keywords = get_all_keywords()
    filtered = []
    for item in all_news:
        title = item['title']
        matched = [kw for kw in keywords if kw in title]
        if matched:
            item['matched_keywords'] = matched
            filtered.append(item)
    
    if filtered:
        print(f"  → 筛选后: {len(filtered)}/{len(all_news)} 条外贸相关")
    return filtered

# ============= 数据源 3: 化工品价格数据（超越微舆的核心能力） =============
def collect_chemical_prices():
    """采集化工品实时价格数据"""
    import akshare as ak
    
    results = []
    try:
        # 原油价格
        crude = ak.futures_foreign_hist(symbol="SC", start_date=date_str, end_date=date_str)
        if not crude.empty:
            latest = crude.iloc[-1]
            results.append({"name": "上海原油SC", "price": float(latest.get('close', 0)), "unit": "元/桶"})
    except: pass
    
    try:
        # 汇率
        rate = ak.currency_latest()
        usd = rate[rate['code'] == 'USD']
        if not usd.empty:
            results.append({"name": "USD/CNY", "price": float(usd.iloc[-1].get('rate', 0)), "unit": "人民币"})
    except: pass
    
    print(f"  ✓ 化工品价格: {len(results)} 项实时数据")
    return results

# ============= 主流程 =============
async def main():
    print(f"\n{'='*50}")
    print(f"  🚀 超越微舆 - 统一数据采集 {date_str}")
    print(f"{'='*50}\n")
    
    # 1. TrendRadar（深度新闻）
    print("▶ 数据源 1: TrendRadar 深度新闻")
    trendradar_news = collect_from_trendradar()
    
    # 2. BettaFish（社交舆情）  
    print("\n▶ 数据源 2: BettaFish 社交舆情")
    bettafish_news = await collect_from_bettafish()
    
    # 3. 化工品价格
    print("\n▶ 数据源 3: 化工品实时价格")
    chemical_prices = collect_chemical_prices()
    
    # ============= 合并与去重 =============
    all_news = trendradar_news + bettafish_news
    seen_titles = set()
    unique_news = []
    for item in all_news:
        t = item['title'].strip()[:50]
        if t not in seen_titles:
            seen_titles.add(t)
            unique_news.append(item)
    
    # ============= 保存结果 =============
    output = {
        "date": date_str,
        "timestamp": datetime.datetime.now().isoformat(),
        "summary": {
            "trendradar": len(trendradar_news),
            "bettafish": len(bettafish_news),
            "chemical_prices": len(chemical_prices),
            "total_unique": len(unique_news)
        },
        "trendradar_news": trendradar_news,
        "bettafish_news": bettafish_news,
        "chemical_prices": chemical_prices,
        "keywords_used": TRADE_KEYWORDS_V2
    }
    
    output_file = OUTPUT_DIR / f"unified_data_{date_str}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*50}")
    print(f"  📊 采集汇总")
    print(f"  TrendRadar 新闻: {len(trendradar_news)} 条")
    print(f"  BettaFish 舆情: {len(bettafish_news)} 条")
    print(f"  化工品价格: {len(chemical_prices)} 项")
    print(f"  去重后总计: {len(unique_news)} 条")
    print(f"  输出文件: {output_file}")
    print(f"{'='*50}\n")
    
    return output

if __name__ == "__main__":
    asyncio.run(main())
