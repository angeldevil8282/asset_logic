import pandas as pd
import yfinance as yf
import json
import os
from datetime import datetime

def run_logic():
    # 1. 銘柄リストをリポジトリ内から読み込む
    input_path = 'data/stocks.json'
    
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        stocks = json.load(f)

    if not stocks:
        print("No stocks to track.")
        return

    # 2. 株価データの取得（yfinance）
    tickers = [f"{s['code']}.T" for s in stocks]
    print(f"{len(tickers)} 銘柄のデータを取得中...")
    
    data = yf.download(tickers, period="2d", auto_adjust=True)

    # 3. 前日比(%)を計算
    last_rows = data['Close']
    changes_dict = {}

    for ticker in tickers:
        try:
            s = last_rows[ticker].dropna()
            if len(s) >= 2:
                change = ((s.iloc[-1] / s.iloc[-2]) - 1) * 100
                code = ticker.replace('.T', '')
                changes_dict[code] = round(change, 2)
            else:
                changes_dict[ticker.replace('.T', '')] = 0.0
        except Exception as e:
            changes_dict[ticker.replace('.T', '')] = 0.0

    # 4. 結果を results.json として保存（Actionsがこれを拾ってダッシュボードへ送る）
    with open('results.json', 'w', encoding='utf-8') as f:
        json.dump(changes_dict, f, indent=2)

    print(f"完了！ 実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    run_logic()
