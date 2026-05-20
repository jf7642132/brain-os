#!/usr/bin/env python3
import json

with open('/root/.hermes/projects/trade-risk-alert/data/south_america_africa_trade_data.json') as f:
    data = json.load(f)

# Enrich with latest 2026 Q1 data
data['meta']['last_updated'] = '2026-05-02T22:55:00+08:00'
data['meta']['status'] = 'enhanced'
data['meta']['update_note'] = '2026 Q1 海关数据补充 + 南美/非洲新增国家'

# Update South America summary
data['south_america']['summary'] = (
    '南美化工进口市场约1000亿美元，巴西占68%为最大市场。'
    '2026Q1中国对拉美进出口增长15.4%，拉美主要经济体出口持续走强。'
    '阿根廷、巴西和智利2025年出口均创历史新高或接近历史高位。'
    '中国是南美最大的化工品进口来源国。'
)

# Add Peru
data['south_america']['countries']['peru'] = {
    'name_cn': '秘鲁',
    'total_trade_with_china_2025': None,
    'trade_note': '2026Q1中国对秘鲁进出口增长超20%，亚拉陆海新通道高效运营',
    'key_industries': ['铜矿', '锂矿', '渔业'],
    'opportunity': '矿业化学品需求增长快，中秘自贸协定升级推进中，钱凯港投用提升物流效率',
    'risk_factors': ['政治波动', '社区关系风险'],
    'data_sources': ['中国海关总署', '秘鲁外贸旅游部']
}

# Add Colombia
data['south_america']['countries']['colombia'] = {
    'name_cn': '哥伦比亚',
    'total_trade_with_china_2025': None,
    'trade_note': '2026Q1中国对哥伦比亚进出口增长超20%',
    'key_industries': ['石油', '矿业', '化工'],
    'opportunity': '基础设施投资催生化工需求，美国关税压力下对华贸易依存度提升',
    'key_chemical_import_products': ['塑料原料', '有机化学品', '化肥'],
    'risk_factors': ['安全局势', '物流基础设施待完善'],
    'data_sources': ['中国海关总署', '哥伦比亚国家统计局']
}

# Update Africa summary
data['africa']['summary'] = (
    '2025年中非贸易额达2.49万亿元(约3450亿美元)，较2000年增长27.5倍。'
    '2026Q1中非贸易达6465.6亿元(约923亿美元)，同比增长23.7%。'
    '化工塑料制品(HS28-40项)1749亿元(约240亿美元)，增速19.9%。'
    '2026年5月1日起中国对53个非洲建交国全面实施商品零关税。'
    '中国对非洲出口中间品增长23.3%，资本品增长43.5%，消费品增长25%(2026Q1)。'
)

# Add Morocco
data['africa']['countries']['morocco'] = {
    'name_cn': '摩洛哥',
    'chemical_import_estimate': None,
    'import_from_china_note': '非洲第四大中国进口国，2024年贸易额快速增长',
    'key_demand': '汽车产业(雷诺/Stellantis工厂)带动化工品需求，磷酸盐加工化学品',
    'risk_factors': ['西撒哈拉地缘风险', '欧盟贸易竞争'],
    'opportunity': '汽车产业链外溢带来化工中间体需求，北非工业制造中心，对欧出口跳板',
    'data_sources': ['中国海关总署', '摩洛哥外汇管理局', 'ExportFocus Africa']
}

# Add Algeria
data['africa']['countries']['algeria'] = {
    'name_cn': '阿尔及利亚',
    'chemical_import_estimate': None,
    'import_from_china_note': '非洲第五大中国进口国，2024年进口额约$5bn+',
    'key_demand': '重型机械配套化工品，能源产业化学品，建筑用塑料/涂料',
    'risk_factors': ['外汇管制严格', '经济依赖油气'],
    'opportunity': '公共基础设施投资带动化学品需求，中阿产能合作稳步推进',
    'data_sources': ['中国海关总署', '阿尔及利亚海关', 'ExportFocus Africa']
}

# Add Kenya
data['africa']['countries']['kenya'] = {
    'name_cn': '肯尼亚',
    'chemical_import_estimate': None,
    'import_from_china_note': '东非最大中国进口国，消费品和工业品并重',
    'key_demand': '建材化学品(水泥/涂料/塑料)，农化产品(化肥/农药)',
    'risk_factors': ['外汇短缺', '电力供应不稳定'],
    'opportunity': '东非门户蒙巴萨港辐射东共体市场，基建快速发展，蒙内铁路经济走廊效应持续',
    'data_sources': ['ExportFocus Africa', '中国海关总署', '肯尼亚国家统计局']
}

# Update regional trends with latest data
data['africa']['regional_trends']['china_africa_trade_q1_2026'] = '2026Q1中非贸易6465.6亿元(约$92.3B)，同比+23.7%，创2022年以来最高增速'
data['africa']['regional_trends']['china_latam_trade_q1_2026'] = '2026Q1中国对拉美进出口增速15.4%，与东盟(15.4%)、非洲(23.7%)均保持两位数增长'
data['africa']['regional_trends']['china_africa_zero_tariff_2026'] = '2026年5月1日起中国对53个非洲建交国全面实施零关税，全球首个主要经济体对非全覆盖'
data['africa']['regional_trends']['africa_chemical_growth_outlook'] = '非洲和中东化工产量增速由2025年2.3%提升至3.8%(2026)，成为增速最快区域'
data['africa']['regional_trends']['key_growth_drivers'].append('2026年5月起53个非洲国家零关税政策，大幅降低进口成本，刺激双边贸易')

# Update action items
for a in data.get('action_items', []):
    if a['item'] == '添加南美/非洲关键词到数据采集流水线':
        a['status'] = 'done'
        a['description'] = '已在TRADE_KEYWORDS_V2中新增"emerging_markets"分类，覆盖巴西/南美/非洲各国及中国-非洲合作相关关键词'
    if a['item'] == '建立南美化工贸易日报采集':
        a['status'] = 'in_progress'
        a['description'] = '已建立南美/非洲贸易数据结构框架，涵盖6南美+6非洲国家。日报采集需等待数据源API集成'

with open('/root/.hermes/projects/trade-risk-alert/data/south_america_africa_trade_data.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

sa = list(data['south_america']['countries'].keys())
af = list(data['africa']['countries'].keys())
print(f'Data file updated!')
print(f'South America ({len(sa)}): {sa}')
print(f'Africa ({len(af)}): {af}')
print(f'Regional trends: {len(data["africa"]["regional_trends"])} keys')
print(f'Action items: {len(data.get("action_items", []))}')
print(f'File: /root/.hermes/projects/trade-risk-alert/data/south_america_africa_trade_data.json')
