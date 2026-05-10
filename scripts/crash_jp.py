import yfinance as yf
import pandas as pd
import json
import os
from datetime import datetime

# 設定ファイルとデータ保存先のパス
CONFIG_PATH = 'data/crash_jp.json'
# my_dashboardリポジトリ側に書き出すパス（環境に合わせて調整）
OUTPUT_DATA_PATH = '../my_dashboard/crash_jp/data/daily_changes.json'

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

def check_and_notify(results):
    alert_messages = []
    for r in results:
        # 銘柄個別の閾値を超えているか判定
        if r['change_pct'] <= r['target_down']:
            diff_text = f"あと {r['diff_to_target']:.0f}円" if r['diff_to_target'] > 0 else "🎯目標到達！"
            msg = (
                f"⚠️【急落検知】{r['name']}\n"
                f"騰落: {r['change_pct']}% (閾値: {r['target_down']}%)\n"
                f"現在: {r['current_price']:,}円\n"
                f"目標: {r['reference_price']:,}円 ({diff_text})"
            )
            alert_messages.append(msg)
    
    if alert_messages:
        full_message = "\n\n".join(alert_messages)
        print(full_message)
        # ここにDiscordやLINEへの通知関数を呼び出す（SBI版の流用）
    else:
        print("閾値を超えた銘柄はありません。")

def main():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    data = get_stock_data(config['tickers'])
    
    # ダッシュボード用に保存
    os.makedirs(os.path.dirname(OUTPUT_DATA_PATH), exist_ok=True)
    with open(OUTPUT_DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump({"date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "stocks": data}, f, indent=4, ensure_ascii=False)
    
    # アラート判定
    check_and_notify(data)

if __name__ == "__main__":
    main()
