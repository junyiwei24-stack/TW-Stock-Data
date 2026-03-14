import pandas as pd
import requests
from datetime import datetime, timedelta
import os

# 1. 取得台灣時間 (UTC+8)
tw_now = datetime.utcnow() + timedelta(hours=8)
date_str = tw_now.strftime("%Y-%m-%d")
# TradingView 規定的 ISO 8601 格式
tv_time_str = tw_now.strftime("%Y-%m-%dT00:00:00Z")

print(f"啟動爬蟲，準備抓取 {date_str} 的大盤融資餘額...")

# 2. 使用 FinMind 免費 API 抓取大盤 (TAIEX) 融資券餘額
url = f"https://api.finmindtrade.com/api/v4/data?dataset=TaiwanStockMarginPurchaseShortSale&data_id=TAIEX&start_date={date_str}"

try:
    response = requests.get(url)
    data = response.json()
    
    # 檢查今天是否有開盤/是否有資料
    if data['msg'] == 'success' and len(data['data']) > 0:
        # 取出今天的「融資餘額」數值
        latest_margin_value = data['data'][-1]['MarginPurchaseBalance']
        print(f"✅ 抓取成功！今日融資餘額: {latest_margin_value}")
    else:
        print("⚠️ 今日無資料 (可能為假日、尚未更新，或無交易)")
        exit(0) # 正常結束程式，不寫入檔案
        
except Exception as e:
    print(f"❌ 抓取失敗: {e}")
    exit(1)

# 3. 讀取我們剛剛建立的 CSV 檔案
csv_file = 'margin_balance.csv'
if os.path.exists(csv_file):
    df = pd.read_csv(csv_file)
else:
    df = pd.DataFrame(columns=['time', 'value'])

# 4. 檢查今天是否已經更新過，避免重複寫入
if not df.empty and df.iloc[-1]['time'] == tv_time_str:
    print("今日資料已存在 CSV 中，無需重複更新。")
else:
    # 5. 將最新資料加入 DataFrame 並存檔
    new_row = pd.DataFrame({'time': [tv_time_str], 'value': [latest_margin_value]})
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(csv_file, index=False)
    print("✅ 成功將最新融資資料寫入 margin_balance.csv！")
