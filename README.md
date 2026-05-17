https://angeldevil8282.github.io/my_dashboard/

＜ディレクトリ構造＞
①SBI高配当用
②日経 暴落監視用
③米国株 暴落監視用

リポジトリ(1)（angeldevil8282/asset_logic）
└─ asset_logic/ (既存：①SBI高配当用)
    ├── data/
    │   ├─ sbi.json (対象101銘柄)
    │   ├─ crash_jp.json (②日経平均、個別銘柄(任天堂等)の閾値)
    │   └─ crash_us.json (③QQQ、GAFAM、AVGO/TSMC/NVDA：メガテックの閾値)
    ├── scripts/
    │   ├─ sbi.py
    │   ├─ crash_jp.py (既存のupdate_assets.pyをベースに改造)
    │   └─ crash_us.py (既存のupdate_assets.pyをベースに改造)
    └── .github/workflows/
         ├─ sbi.yml (既存：15:15等の定時実行)
         ├─ crash_jp.yml   (新規：日中15分おき実行)
         └─ crash_us.yml   (新規：深夜1時間おき実行)

リポジトリ(2)（angeldevil8282/my_dashboard）
└─ my_dashboard/ 
    ├─── index.html　(選択：①、②、③)
    ├── sbi/    
    │   ├─ index.html (①SBI高配当用)
    │   ├ data/
    │   │├ daily_changes.json
    │   │├ config.json
    │   │└ summary.json
    │   └ logs/
    │     ├ changes_YYYY-MM-DD_HHMMSS.json (既存：ログ)
    │     └ summary_YYYY-MM-DD_HHMMSS.json (既存：ログ)
    ├── crash_jp/
    │   ├─ index.html (②日経平均、個別銘柄の閾値)
    │   ├ data/
    │   │├ daily_changes.json
    │   │├ config.json
    │   │└ summary.json
    │   └ logs/
    │     ├ changes_YYYY-MM-DD_HHMMSS.json (既存：ログ)
    │     └ summary_YYYY-MM-DD_HHMMSS.json (既存：ログ)
    └── crash_us/
         ├─ index.html (③QQQ、GAFAM、AVGO/TSMC/NVDA：メガテックの閾値)
         ├ data/
         │├ daily_changes.json
         │├ config.json
         │└ summary.json
         └ logs/
           ├ changes_YYYY-MM-DD_HHMMSS.json (既存：ログ)
           └ summary_YYYY-MM-DD_HHMMSS.json (既存：ログ)
