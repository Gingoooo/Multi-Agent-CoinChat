# Multi-Agent-Coinchat


## 專案簡介

一個基於 LangGraph 框架打造的記帳助手,能夠協助使用者記錄和查詢交易資訊。

## 專案特色

- 🤖 多代理系統架構
  - Intent Checker Agent: 負責理解用戶意圖
  - Insert Agent: 處理交易記錄的新增
  - Query Agent: 處理交易記錄的查詢
- 📝 自然語言互動
- 🗄️ SQLite 本地數據存儲

## 系統需求

- Python 3.12+
- Google Gemini API 金鑰

## 安裝與執行

請依以下步驟安裝並執行專案。

### 1. Clone 專案

使用 Git 將專案複製到本地：

```bash
git clone https://github.com/[your-username]/multi-agent-coinchat.git
cd multi-agent-coinchat
```

### 2. 建立虛擬環境

為了保持依賴的獨立性，建議使用虛擬環境：

```bash
python -m venv venv
source venv/bin/activate  # Windows 用戶使用 `venv\Scripts\activate`
```

### 3. 配置環境變數

將範例檔案複製為 `.env`，並將 Gemini API 金鑰添加到 .env 檔案中：

建立 `.env` 檔案，並添加以下內容以設定必要的環境變數：

```bash
cp .env.example .env
```

編輯 .env 檔案，添加以下內容：

```
API_KEY=your_gemini_api_key
```

安裝套件以讀取 `.env` 檔案（已在 `requirements.txt` 中包含）。

### 4. 安裝依賴套件

使用 `requirements.txt` 安裝必要的依賴：

```bash
pip install -r requirements.txt
```

### 5. 初始化資料庫

執行 `db/db_init.py` 初始化資料庫：

```bash
python db_init.py
```

### 6. 執行應用程式

```bash
python multi-agent.py
```

### 7. 開始對話

- 記錄交易: "幫我記錄今天買咖啡花了 80 元"
- 查詢交易: "這個月的支出總共多少?"


## 系統需求

建議使用 Python 3.12 或以上版本，以確保最佳相容性與性能。


## 資料夾結構

```
project/
├── README.md
├── requirements.txt
├── .env.example
├── .env
├── .gitignore
├── multi-agent.py
├── config.py
├── tools.py
├── prompts.py
└── db/
    ├── __init__.py
    ├── db_init.py
    └── bookkeeper.db
```
