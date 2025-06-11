import re
from flask import Blueprint, Response, json, jsonify, request
from routes.GoodDetail import toggle_track_status  # 匯入函式
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from models.models import Client, Client_Favorites
from routes.RegisterPage import is_valid_account, is_valid_password
from sqlalchemy.orm import Session
from dbconfig.dbconnect import db
from werkzeug.security import generate_password_hash

clientPage_bp = Blueprint("clientPage", __name__, url_prefix="/clientPage")

'''
 * 基本參數驗證：非字串型態& 齊全
 * 防止無效
'''

#-------------------------------------#
#      call /GoodDetail/track func    #
#-------------------------------------#
@clientPage_bp.route("/track", methods=["POST"])
def clientpage_toggle_track():
    return toggle_track_status()  # 重用邏輯


@clientPage_bp.route("/trackList", methods=["POST"])
def get_track_list():
    try:
        data = request.get_json()
        cId = data.get('cId')

        # 基本參數驗證：非字串型態& 齊全
        if not cId or not isinstance(cId, str):
            return jsonify({"error": "請求參數錯誤"}), 400

        # Select * from Client_Favorites WHERE cId = ?
        track = Client_Favorites.query.filter(Client_Favorites.cId == cId).all()

        # 防止無效
        if not track:
            return jsonify({"error": "未找到資源"}), 404
        
        # Track might be an array of objects
        # Using for loop to get data
        result = [
                    {
                        "cId": item.cId,
                        "pId": item.pId
                    }
                    for item in track
                ]
        return Response(json.dumps({"results": result}, ensure_ascii=False), mimetype='application/json')

    except SQLAlchemyError as e:
        print(f"!!! SQLAlchemy Error Details: {e}")
        return jsonify({'error': f'資料庫操作錯誤: {str(e)}'}), 500
    except Exception as e:
        print(f"發生未預期錯誤: {e}")
        return jsonify({'error': '伺服器內部錯誤'}), 500


# /client
@clientPage_bp.route("/client", methods=["POST"])
def get_client_data():
    try:
        data = request.get_json()
        cId = data.get('cId')
        if not cId or not isinstance(cId, str):
            return jsonify({"error": "請求參數錯誤"})
        
        client_data = Client.query.filter(Client.cId == cId).first()
        client_data_json = {
            "cId": client_data.cId,
            "cName": client_data.cName,
            "account": client_data.account,
            "email": client_data.email,
            "phone": client_data.phone,
            "sex": client_data.sex,
            "birthday": client_data.birthday
        }
        if not client_data:
            return jsonify({"error": "未找到資源"}), 404
        
        return Response(json.dumps({"results": client_data_json}, ensure_ascii=False), mimetype='application/json')

    except SQLAlchemyError as e:
        return jsonify({str(e)}), 500

    except Exception as e:
        print(f"發生未預期錯誤: {e}")
        return jsonify({'error': '伺服器內部錯誤'}), 500


'''
update data欄位是否重複函式
'''
def is_duplicate_account(db: Session, account: str, exclude_id=None):
    query = db.query(Client).filter(Client.account == account)
    if exclude_id:
        query = query.filter(Client.cId != exclude_id)
    return query.first() is not None

def is_duplicate_email(db: Session, email: str, exclude_id=None):
    query = db.query(Client).filter(Client.email == email)
    if exclude_id:
        query = query.filter(Client.cId != exclude_id)
    return query.first() is not None

def is_duplicate_phone(db: Session, phone: str, exclude_id=None):
    query = db.query(Client).filter(Client.phone == phone)
    if exclude_id:
        query = query.filter(Client.cId != exclude_id)
    return query.first() is not None


@clientPage_bp.route("/data/update", methods=["POST"])
def update_client_data():
    try:
        '''
        * 需登入，account + birthday 不可修改
        * 用textfield方式呈現，default value 為原本會員資料
            * 密碼不需要放default value
            * textfeild value不可為空值
        * 送出後要檢查
            * 所有欄位皆為required
            * cName: 1<=長度<=30
            * account:需含大小寫、符號、8<=長度<=20
            * password: 需含大小寫、符號、8<=長度<=20
            * email: >=8,<=20
            * phone: 長度 == 10
            * birthday: 日期<=現在日期
            * account、password、phone、email皆不可重複
        '''

        # 1. 檢查必要欄位
        data = request.get_json()
        required_fields = ["cName", "email", "phone", "sex"]
        missing = [field for field in required_fields if not (field in data and data[field] is not None)]
        if missing:
            return jsonify({"message": f"缺少必要欄位: {', '.join(missing)}"}), 400
        

        # 2. Get data and columns
        '''
        修改密碼可能要另外寫一支API
        '''
        cId = data["cId"]
        cName = data["cName"]
        email = data["email"]
        phone = data["phone"]
        sex = data["sex"]
        
        # 新增物件
        client = Client.query.filter_by(cId=cId).first()
        if not client:
            return jsonify({"message": "查無此會員"}), 404

        # Form Validation

        if not (1 <= len(cName) <= 30):
            return jsonify({"message": "姓名長度必須介於 1 到 30 個字元之間"}), 400
        
        # From Register import func: is_valid_account, is_valid_password
        # Considering move those form validation func into *services/*
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email) or not (8 <= len(email) <= 64):
            return jsonify({"message": "電子郵件格式或長度錯誤 (需 8-64 字元)"}), 400
        if not re.match(r"^[0-9]{10}$", phone):
            return jsonify({"message": "電話號碼必須是 10 位數字"}), 400


        # verify duplicate
        # 這表示在查詢時會排除自己的 cId，也就是排除掉「正在更新的那個人」
        if is_duplicate_email(db.session, email, exclude_id=cId):
            return jsonify({"message": "Email 已存在"}), 400
        if is_duplicate_phone(db.session, phone, exclude_id=cId):
            return jsonify({"message": "電話已存在"}), 400

        # Update
        client.cName = cName
        client.email = email
        client.phone = phone
        client.sex = sex
        
        db.session.commit()
        return jsonify({"message": "會員資料更新成功"}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({str(e)}), 500
    
    except Exception as e:
        db.session.rollback()
        print(f"發生未預期錯誤: {e}")
        return jsonify({'error': '伺服器內部錯誤'}), 500


@clientPage_bp.route("/password/update", methods=["POST"])
def password_update():

    try:
        data = request.get_json()

        cId = data["cId"]
        new_password = data["password"]
        if not new_password or not isinstance(new_password, str):
                return jsonify({"error": "請求參數錯誤"}), 400

        if not is_valid_password(new_password):
                return jsonify({"message": "密碼格式錯誤 (需 8-20 字元，包含大小寫字母及符號)"}), 400
                
        password_hash = generate_password_hash(new_password)

        Client.query.filter_by(cId = cId).update({
            Client.password_hash: password_hash
        })
        db.session.commit()

        return jsonify({"message": "successfully modify password", "cId": cId}), 200

    except OperationalError as oe:
        # 連線超時或資料庫無法操作
        db.session.rollback()
        return jsonify({'error': f'資料庫連線失敗或逾時: {str(oe)}'}), 500

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': f'資料庫操作錯誤: {str(e)}'}), 500

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'伺服器內部錯誤: {str(e)}'}), 500
