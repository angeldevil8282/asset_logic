import json
import datetime

def calculate_assets():
    # 本来はここでWebスクレイピングやAPIからデータを取ります
    # 今回はテストとして、現在時刻を記録するだけの処理にします
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    data = {
        "last_update": now,
        "status": "Success",
        "message": "15:25の最終監査まであと少し"
    }
    
    # ワークフローが期待するファイル名で保存
    with open('results.json', 'w') as f:
        json.dump(data, f, indent=4)
    
    print(f"Update completed at {now}")

if __name__ == "__main__":
    calculate_assets()
