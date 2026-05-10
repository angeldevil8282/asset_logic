import pandas as pd
import yfinance as yf
import json
import os
from datetime import datetime

# --- 最適化パラメータ ---
SBI_COEFFICIENT = 0.9
SBI_OFFSET = -0.05
# ----------------------

def run_logic():
    # 銘柄リスト読み込み
    input_path = 'data/sbi.json'
    with open(input_path, 'r', encoding='utf-8') as f:
        sbi = json.load(f)

    # 比較用に「現在の最新データ」を読み込んでおく
    # dashboard_dest は Actions側で clone された先のパス
    current_data_path = 'dashboard_dest/sbi/data/daily_changes.json'
    current_changes = {}
    if os.path.exists(current_data_path):
        with open(current_data_path, 'r', encoding='utf-8') as f:
            try:
                current_changes = json.load(f)
            except json.JSONDecodeError:
                # ファイルが空、または壊れている場合は空の辞書として初期化
                print(f"Warning: {current_data_path} is empty or invalid. Initializing as empty dict.")
                current_changes = {}
    else:
        current_changes = {}

    # データ取得
    tickers = [f"{s['code']}.T" for s in sbi]
    data = yf.download(tickers, period="2d", auto_adjust=True)
    last_rows = data['Close']

    new_changes = {}
    total_eval = sum(s['evaluation'] for s in sbi)
    sigma_raw = 0.0
    valid_count = 0
    sector_map = {}

    for s in sbi:
        code = s['code']
        ticker = f"{code}.T"
        try:
            prices = last_rows[ticker].dropna()
            # 2日分の価格が取れており、かつ価格が0でない場合のみ「有効」とする
            if len(prices) >= 2 and prices.iloc[-1] > 0:
                change = ((prices.iloc[-1] / prices.iloc[-2]) - 1) * 100
                new_changes[code] = round(change, 2)
                
                contrib = (s['evaluation'] / total_eval) * change
                sigma_raw += contrib
                valid_count += 1
                
                sec = s['sector']
                sector_map[sec] = sector_map.get(sec, 0.0) + contrib
        except:
            continue

    # 【重要】前回と全く同じなら、ファイルを作らずに終了
    # これにより後続の Git Commit と Discord 通知が自動でスキップされる
    # if new_changes == current_changes:
    #   print("No changes detected in stock prices. Skipping update.")
    #   return

    # 変化がある場合のみ計算して保存
    prediction = (sigma_raw * SBI_COEFFICIENT) + SBI_OFFSET
    summary = {
        "timestamp": datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
        "prediction": round(prediction, 3),
        "coverage": f"{valid_count}/{len(sbi)}",
        "params": {"coeff": SBI_COEFFICIENT, "offset": SBI_OFFSET},
        "sector_stats": sorted([{"name": k, "contrib": round(v, 4)} for k, v in sector_map.items()], 
                               key=lambda x: abs(x['contrib']), reverse=True)
    }

    # 成果物の書き出し
    with open('results.json', 'w') as f:
        json.dump(new_changes, f)
    with open('summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run_logic()
