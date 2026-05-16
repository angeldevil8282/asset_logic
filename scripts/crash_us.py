import yfinance as yf
import pandas as pd
import json
import os
from datetime import datetime

CONFIG_PATH = 'data/crash_us.json'
OUTPUT_DATA_PATH = 'daily_changes.json'
DISCORD_MSG_PATH = 'discord_msg.json'

def get_stock_data(tickers):
    results = []
    for t in tickers:
        stock = yf.Ticker(t['symbol'])
        hist = stock.history(period="2d")
        if len(hist) < 2: continue

        prev_close = hist['Close'].iloc[-2]
        current_price = hist['Close'].iloc[-1]
        change_pct = ((current_price - prev_close) / prev_close) * 100
        diff_to_target = current_price - t['reference_price']
        
        results.append({
            "name": t['name'],
            "symbol": t['symbol'],
            "current_price": round(current_price, 2),
            "change_pct": round(change_pct, 2),
            "reference_price": t['reference_price'],
            "diff_to_target": round(diff_to_target, 2),
            "target_down": t['target_down']
        })
    return results

def create_discord_message(data):
    msg_lines = []
    crash_stocks = [s for s in data if s['change_pct'] <= s['target_down']]
    if not crash_stocks: return None

    for s in crash_stocks:
        mark = "📉" if s['change_pct'] < 0 else "📈"
        
        # 🎯 修正ポイント: インデントを揃え、変数に代入
        if s['diff_to_target'] <= 0:
            target_status = "🎯到達!"
        else:
            target_status = f"あと +${s['diff_to_target']}"
            
        target_info = f"(目標: ${s['reference_price']} / {target_status})"
        
        line = (
            f"🇺🇸 **{s['name']}** ({s['symbol']})\n"
            f"騰落: {s['change_pct']}% {mark}\n"
            f"現在: ${s['current_price']}\n"
            f"{target_info}"
        )
        msg_lines.append(line)

    update_time = datetime.now().strftime("%H:%M")
    content = (
        f"🔥 **【米国株 暴落検知】**\n\n"
        + "\n\n".join(msg_lines) +
        f"\n\n時刻: {update_time} (JST)\n"
        f"🔗 https://angeldevil8282.github.io/my_dashboard/crash_us/"
    )
    return content

def main():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f: config = json.load(f)
    data = get_stock_data(config['tickers'])
    
    with open(OUTPUT_DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump({"date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "stocks": data}, f, indent=4, ensure_ascii=False)

    discord_content = create_discord_message(data)
    if discord_content:
        with open(DISCORD_MSG_PATH, 'w', encoding='utf-8') as f:
            json.dump({"content": discord_content}, f, ensure_ascii=False)

if __name__ == "__main__":
    main()
