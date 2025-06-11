from datetime import datetime
import re
import random
import string
from flask import Blueprint, request, jsonify
from dbconfig.dbconnect import db
from models.models import Client # 假設您的模型名稱是 Client
from sqlalchemy import func, collate
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
register_bp = Blueprint('register', __name__, url_prefix="/registerpage")

# --- 輔助函數 (驗證、產生ID) ---

def is_valid_account(account):
    """檢查帳號格式：8-20字元，需包含大小寫字母和符號"""
    pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*()_+={}:;,.<>?/~]).{8,20}$"
    return bool(re.match(pattern, account))

def is_valid_password(password):
    """檢查密碼格式：8-20字元，需包含大小寫字母和符號"""
    pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*()_+={}:;,.<>?/~]).{8,20}$"
    return bool(re.match(pattern, password))

# 修改 generate_client_id 以使用 SQLAlchemy
def generate_client_id():
    """產生唯一的客戶 ID (使用 SQLAlchemy 檢查資料庫)"""
    while True:
        letter = random.choice(string.ascii_lowercase)
        numbers = ''.join(random.choices('0123456789', k=7))
        client_id = f"{letter}{numbers}"
        try:
            # 使用 SQLAlchemy 查詢檢查 cId 是否已存在
            exists = db.session.query(Client.cId).filter_by(cId=client_id).first() is not None
            if not exists:
                return client_id
        except Exception as e: # 捕捉查詢時可能發生的錯誤
            print(f"檢查客戶 ID 唯一性時發生錯誤: {e}")
            # 發生錯誤時拋出，讓上層處理
            raise 

# --- 使用 SQLAlchemy 的註冊路由 ---

@register_bp.route("/register", methods=["POST"])
def register():
    """
    /register: 驗證註冊表單，並使用 SQLAlchemy 將資料插入 Client 資料表
    """
    data = request.get_json()
    try:
        # 1. 檢查必要欄位 (與之前相同)
        required_fields = ["cName", "account", "password", "email", "phone", "sex", "birthday"]
        missing = [field for field in required_fields if not (field in data and data[field] is not None)]
        if missing:
            return jsonify({"message": f"缺少必要欄位: {', '.join(missing)}"}), 400

        # 2. 解析欄位值 (與之前相同)
        cName = data["cName"]
        account = data["account"]
        password = data["password"] # !! 強烈建議雜湊此密碼 !!
        email = data["email"]
        phone = data["phone"]
        sex = data["sex"]
        birthday_str = data["birthday"]


        # 3. 驗證欄位格式 (與之前相同)
        if not (1 <= len(cName) <= 30):
            return jsonify({"message": "姓名長度必須介於 1 到 30 個字元之間"}), 400
        if not is_valid_account(account):
            return jsonify({"message": "帳號格式錯誤 (需 8-20 字元，包含大小寫字母及符號)"}), 400
        if not is_valid_password(password):
             return jsonify({"message": "密碼格式錯誤 (需 8-20 字元，包含大小寫字母及符號)"}), 400
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email) or not (8 <= len(email) <= 64):
            return jsonify({"message": "電子郵件格式或長度錯誤 (需 8-64 字元)"}), 400
        if not re.match(r"^[0-9]{10}$", phone):
            return jsonify({"message": "電話號碼必須是 10 位數字"}), 400
        try:
            birthday = datetime.fromisoformat(birthday_str.replace('Z', '+00:00'))
            if birthday > datetime.now(birthday.tzinfo):
                 return jsonify({"message": "生日必須是過去的日期"}), 400
        except ValueError:
             return jsonify({"message": "生日日期格式錯誤 (應為 ISO 8601 格式，例如 YYYY-MM-DDTHH:MM:SSZ)"}), 400

        # 4. 使用 SQLAlchemy 檢查資料唯一性
        #    帳號檢查 (大小寫區分，使用 collate)
        account_exists = db.session.query(Client.account).filter(
            Client.account.collate('Latin1_General_CS_AS') == account
        ).first()
        if account_exists:
            return jsonify({"message": "此帳號已被註冊 (區分大小寫)"}), 409

        #    Email 檢查 (不分大小寫，使用 func.lower)
        email_exists = db.session.query(Client.email).filter(
            func.lower(Client.email) == func.lower(email)
        ).first()
        if email_exists:
            return jsonify({"message": "此電子郵件已被註冊"}), 409

        #    電話檢查 (直接比對)
        phone_exists = db.session.query(Client.phone).filter_by(phone=phone).first()
        if phone_exists:
            return jsonify({"message": "此電話號碼已被註冊"}), 409

        # 5. 產生唯一的客戶 ID
        client_id = generate_client_id()
        password_hash = generate_password_hash(password)

        # 6. 建立 Client 物件
        #    !! 再次提醒：password 應進行雜湊處理 !!
        new_client = Client(
            cId=client_id,
            cName=cName,
            account=account,
            password_hash=password_hash, # 使用正確的參數名稱儲存雜湊後的密碼
            email=email,
            phone=phone,
            sex=sex,
            birthday=birthday
            # 確保 Client 模型的屬性名稱與這裡使用的鍵名一致
        )

        # 7. 將新物件加入 Session 並提交
        db.session.add(new_client)
        db.session.commit()

        print(f"使用者 {cName} (ID: {client_id}) 已成功寫入資料庫 (ORM)。")
        return jsonify({"message": "註冊成功", "clientId": client_id}), 201

    except IntegrityError as int_err:
        # 捕捉可能的唯一性約束衝突 (雖然前面已檢查，但併發情況下可能發生)
        db.session.rollback() # 回滾交易
        print(f"資料庫完整性錯誤: {int_err}")
        # 判斷是哪個欄位衝突可能比較複雜，這裡返回通用訊息
        return jsonify({"message": "註冊失敗，提供的帳號、Email 或電話可能已被使用。"}), 409
    except Exception as e:
        # 捕捉其他可能的錯誤 (例如資料庫連線問題、ID 生成錯誤等)
        db.session.rollback() # 回滾交易
        print(f"註冊過程中發生未預期錯誤: {e}")
        return jsonify({"message": f"註冊過程中發生錯誤: {e}"}), 500

    # 移除 finally 區塊，SQLAlchemy 會管理 Session

