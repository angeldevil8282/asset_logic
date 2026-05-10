import yfinance as yf
import pandas as pd
import json
import os
from datetime import datetime

# 設定ファイルとデータ保存先のパス
CONFIG_PATH = 'data/crash_jp.json'
# カレントディレクトリに書き出す（YAML側で配送する）
OUTPUT_DATA_PATH = 'daily_changes.json'
DISCORD_MSG_PATH = 'discord_msg.json'

def get_stock_data(tickers):
    results = []
    for t in tickers:
        stock = yf.Ticker(t['symbol'])
        # 騰落率計算のために最新2日分を取得
        hist = stock.history(period="2d")
        if len(hist) < 2: continue

        prev_close = hist['Close'].iloc[-2]
        current_price = hist['Close'].iloc[-1]
        change_pct = ((current_price - prev_close) / prev_close) * 100
        
        diff_to_target = current_price - t['reference_price']
        
        results.append({
            "name": t['name'],
            "symbol": t['symbol'],
            "current_price": round(current_price, 1),
            "change_pct": round(change_pct, 2),
            "reference_price": t['reference_price'],
            "diff_to_target": round(diff_to_target, 1),
            "target_down": t['target_down']
        })
    return results

def create_discord_message(data):
    msg_lines = []
    for s in data:
        # 騰落率に応じたマーク
        mark = "▼" if s['change_pct'] < 0 else "▲"
        
        # 個別閾値に基づく状況判定
        is_crash = s['change_pct'] <= s['target_down']
        status = "急落（閾値超過）" if is_crash else "監視中"
        
        # 目標価格までの距離
        if s['diff_to_target'] <= 0:
            target_info = f"(目標: {s['reference_price']:,}円 / 🎯目標到達！)"
        else:
            target_info = f"(目標: {s['reference_price']:,}円 / あと +{s['diff_to_target']:,}円)"

        line = (
            f"**{s['name']}** ({s['symbol']})\n"
            f"状況: {status}\n"
            f"騰落: {s['change_pct']}% {mark}\n"
            f"現在: {s['current_price']:,}円\n"
            f"{target_info}"
        )
        msg_lines.append(line)

    stocks_summary = "\n\n".join(msg_lines)
    update_time = datetime.now().strftime("%H:%M")
    # GitHub Actionsの実行番号を取得
    run_num = os.environ.get('GITHUB_RUN_NUMBER', '0')

    content = (
        f"⚠️ **【日本株 暴落監視】[#{run_num}]**\n\n"
        f"{stocks_summary}\n\n"
        f"時刻: {update_time}\n"
        f"🔗 Dashboard: https://angeldevil8282.github.io/my_dashboard/crash_jp/"
    )
    return content

def main():
    # 1. 設定読み込み
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 2. データ取得
    data = get_stock_data(config['tickers'])
    
    # 3. ダッシュボード用JSON保存
    dir_name = os.path.dirname(OUTPUT_DATA_PATH)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    
    with open(OUTPUT_DATA_PATH, 'w', encoding='utf-8') as f:
        output_json = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "stocks": data
        }
        json.dump(output_json, f, indent=4, ensure_ascii=False)

    # 4. Discord用リッチメッセージ生成 & 保存
    discord_content = create_discord_message(data)
    with open(DISCORD_MSG_PATH, 'w', encoding='utf-8') as f:
        json.dump({"content": discord_content}, f, ensure_ascii=False)

    # コンソール出力（ログ確認用）
    print(discord_content)

if __name__ == "__main__":
    main()
