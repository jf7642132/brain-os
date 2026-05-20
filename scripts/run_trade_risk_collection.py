#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
「超越微舆」每日数据采集任务 v3.0
用于 Cron Job 自动执行（每天 9:00 / 14:00 / 20:00）
"""
import subprocess
import sys
from pathlib import Path
from datetime import datetime

UNIFIED_PIPELINE = Path("/root/.hermes/scripts/unified_data_pipeline.py")

def run_collection():
    print(f"🚀 超越微舆 - 统一数据采集")
    print(f"⏰ 执行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        result = subprocess.run(
            ["python3", str(UNIFIED_PIPELINE)],
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.stdout:
            print(result.stdout)

        if result.stderr:
            print("⚠️ 错误信息：")
            print(result.stderr)

        # 检查统一输出目录
        unified_dir = Path("/root/.hermes/projects/trade-risk-alert/data/unified")
        today_slug = datetime.now().strftime("%Y-%m-%d")
        output_file = unified_dir / f"unified_data_{today_slug}.json"
        if output_file.exists():
            size = output_file.stat().st_size
            print(f"✅ 输出文件：{output_file} ({size} bytes)")
        else:
            print(f"⚠️ 输出文件未生成：{output_file}")

        print("\n✅ 采集任务完成！")

        # 采集完成后自动触发预警推送检查
        print("\n🔔 运行预警推送检查...")
        push_script = Path("/root/trade_risk_alert/push_bridge.py")
        if push_script.exists():
            push_result = subprocess.run(
                ["python3", str(push_script)],
                capture_output=True,
                text=True,
                timeout=60
            )
            if push_result.stdout:
                print(push_result.stdout)
            if push_result.stderr:
                print("⚠️ 推送错误：")
                print(push_result.stderr)

        return True

    except subprocess.TimeoutExpired:
        print("❌ 采集任务超时（300秒）")
        return False
    except Exception as e:
        print(f"❌ 执行失败：{e}")
        return False

if __name__ == "__main__":
    success = run_collection()
    sys.exit(0 if success else 1)
