## 6/11更新日誌

- Click times 儲存至redis(30分鐘一次回傳database)

- GoodPage , HomePage 資料快取12小時 (由clicktimes 排序不想 cache 那麼快刷新)

- 新增 APScheduler 排程任務：每 30 分鐘自動將 Redis 中累積的點擊數批次寫回資料庫，確保資料最終一致。

- 新增 JWT 登出機制：
每次登入產出新的 access 和 refresh token, /loginpage/logout API，使用者登出時，將當前 JWT token 加入 Redis 黑名單，確保登出後該 token 立即失效。

- 黑名單驗證
在 token_required 裝飾器中加入黑名單檢查，所有需要驗證的 API 都會自動拒絕已登出的 token。。


# Flask SQLAlchemy 後端 API 專案

1. 命名規則以 "TagPath.py" ，記得分大小寫 (FrameSearch.py) url_prefix="當前功能主路徑"

2. requirements.txt 為所有運作API必要函式

3. 如果該功能path較多，請在每個path註解功能

4. 寫法沒有硬性規定，能動就好ㄏ ，唯一要注意的是要抓的參數要跟model上資料表的一樣

## 使用的 Libraries
直接 pip install -r requirements.txt

*   **語言:** Python 3.11.4
*   **框架:** Flask
*   **ORM:** SQLAlchemy (搭配 Flask-SQLAlchemy)
*   **資料庫:** Microsoft SQL Server (透過 SQLAlchemy  驅動程式連接)
*   **API 文件:** OpenAPI (Swagger) - `APISet.yaml`
*   **Hash:** werkzeug.security

## 專案目錄結構

```bash
serverclient/
 └── │── main.py                     # Flask 應用程式進入點，註冊藍圖
     │── routes/                     # API 路由藍圖 (Blueprints)
     │   │── Frame.py                # 框架/搜尋相關
     │   │── HomePage.py             # 首頁相關
     │   │── LoginPage.py            # 登入處理
     │   │── RegisterPage.py         # 註冊處理
     │   │── GoodPage.py             # 商品列表相關
     │   │── ClientPage.py           # 用戶個人資訊
     │   └── GoodDetail.py           # 商品詳細資訊相關
     │
     │── models/                     # SQLAlchemy 資料庫模型定義
     │   └── models.py               # 包含 Product, Client, Price_Now 等模型
     │── dbconfig/
     │   │── redisconfig.py          # redis connect config
     │   │── Scheduler.py            # 排程 批次回傳clicktimes 
     │   └── dbconnect.py            # 資料庫連線設定 (SQLAlchemy DB URI) 與 db 物件初始化
     │── dbconfig/
     │   └── auth.py                 # JWT 驗證
     │
     │── .env                        # 儲存token_key
     │── requirements.txt            # Python 依賴套件列表
     │── APIset.yaml                 # OpenAPI 規格文件
     │── README.md                   # 本文件
     └── ...
```

## 安裝與設定


## 目錄
--Tag
- [框架功能 (Frame)]
- [首頁功能 (HomePage)]
- [登入功能 (LoginPage)]
- [註冊功能 (RegisterPage)]
- [商品清單功能 (GoodPage)]
- [商品詳情功能 (GoodDetail)]
- [使用者個人頁面功能 (ClientPage)]

2.  **建立並啟用虛擬環境 (建議):**
    ```bash
    python -m venv .venv
    # Windows
    .\.venv\Scripts\activate
    # macOS/Linux
    source .venv/bin/activate
    ```
3.  **安裝依賴:**
    ```bash
    pip install -r requirements.txt
    ```
    *(`requirements.txt` 應包含所有必要的函式庫，建議使用 `pip freeze > requirements.txt` 產生)*

4.  **設定資料庫連線:**
    *   開啟 `dbconfig/dbconnect.py` 檔案。
    *   修改 `DB_USERNAME`, `DB_PASSWORD`, `DB_SERVER`, `DB_NAME`, `DB_DRIVER` 等變數，填入您實際的 Microsoft SQL Server 連線資訊。
    *   **重要:** 請確保不要將敏感的密碼直接提交到版本控制系統中。考慮使用環境變數或其他更安全的方式管理密碼。

5.  **資料庫初始化 (如果需要):**
    *   確保您的 SQL Server 資料庫已建立。
    *   如果使用了資料庫遷移工具 (如 Flask-Migrate)，請執行相應的遷移指令。如果沒有，請確保資料庫結構與 `models/models.py` 中的定義相符。

## 執行應用程式

在虛擬環境啟用且設定完成後，執行以下指令啟動 Flask 開發伺服器：

```bash
python main.py
```

伺服器預設會在 `http://127.0.0.1:5000/` 或 `http://localhost:5000/` 上運行。

## API 端點說明

以下是主要的 API 端點摘要。更詳細的請求/回應格式、參數說明請參考 `APISet.yaml` 文件。

---

### 框架功能 (Frame) - `/frame`

*   **POST `/frame/search`**: 根據關鍵字搜尋商品 (商品名稱或品牌)。

### 首頁功能 (HomePage) - `/home`

*   **GET `/home/product`**: 取得商品列表，可選用 `category` 參數篩選，預設按 `clickTimes` 排序。

### 登入功能 (LoginPage) - `/login`

*   **POST `/login/login`**: 驗證使用者帳號密碼。

### 註冊功能 (RegisterPage) - `/register`

*   **POST `/register/register`**: 新使用者註冊。
    *   執行欄位驗證與資料唯一性檢查 (帳號、Email、電話)。
    *   自動產生 Client ID。
    *   *(TODO/注意：原始需求中的郵箱驗證、儲存登入狀態等功能可能尚未完全實現)*

### 商品清單功能 (GoodPage) - `/product`

*   **GET `/product`**: 顯示商品列表 (與首頁 `/home/product` 類似)，可選 `category` 參數，預設按 `clickTimes` 排序。

### 商品詳情功能 (GoodDetail) - `/GoodDetail`

*   **GET `/GoodDetail/product/{pId}`**: 獲取特定商品的詳細資訊。
*   **GET `/GoodDetail/priceNow/{pId}`**: 取得商品在各通路的即時價格資訊。
*   **GET `/GoodDetail/productReview/{pId}`**: 取得商品的評價列表。
*   **POST `/GoodDetail/click/{pId}`**: 記錄商品頁面被點擊一次。
*   **POST `/GoodDetail/track/id`**: 檢查特定使用者是否關注了某商品。
*   **POST `/GoodDetail/track/insert`**: 新增使用者對某商品的關注。
*   **POST `/GoodDetail/track/delete`**: 取消使用者對某商品的關注。


## API 文件

本專案使用 OpenAPI (Swagger) 規格來描述 API。詳細的 API 規格請參閱根目錄下的 `APISet.yaml` 文件。您可以使用 Swagger Editor 或其他相容工具來視覺化和互動測試此文件。

## 錯誤碼說明

*   `200`: 請求成功 / 操作成功。
*   `201`: 資源成功建立 (例如：註冊成功)。
*   `400`: Bad Request - 請求無效，通常是參數錯誤或缺少必要參數。
*   `401`: Unauthorized - 驗證失敗 (例如：帳號密碼錯誤)。
*   `404`: Not Found - 請求的資源不存在。
*   `409`: Conflict - 請求衝突，通常是資源已存在 (例如：帳號/Email 已被註冊)。
*   `500`: Internal Server Error - 伺服器內部發生錯誤。