from flask import Response, Blueprint, jsonify, request
from models.models import Client_Favorites, Good_Review, Product, Price_Now
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from dbconfig.dbconnect import db
from dbconfig.redisconfig import cache
import json

goodDetail_bp = Blueprint("GoodDetail", __name__, url_prefix="/gooddetail")

# /product/<string:pId>
@goodDetail_bp.route("/product/<string:pId>", methods=["GET"])
def get_product_detail(pId):
    try:
        if not pId or not isinstance(pId, str):
            return jsonify({"error": "請求參數錯誤"}), 400

        # select * from Product where pId=?
        product = Product.query.filter(Product.pId == pId).first()

        if not product:
            return jsonify({"error": "未找到資源"}), 404
        
        results = {
            "pId": product.pId,
            "pName": product.pName,
            "brand": product.brand,
            "category": product.category,
            "price": float(product.price),
            "review": float(product.review) if product.review is not None else None,
            "clickTimes": product.clickTimes
        }

        # ensure_ascii=False：讓中文顯示正常
        return Response(json.dumps({"results": results}, ensure_ascii=False), mimetype='application/json')

    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        print(f"發生未預期錯誤: {e}")
        return jsonify({'error': '伺服器內部錯誤'}), 500
    
# /priceNow/<string:pId>
@goodDetail_bp.route("/priceNow/<string:pId>", methods=["GET"])
def get_price_now(pId):
    try:
        if not pId or not isinstance(pId, str):
            return jsonify({"error": "請求參數錯誤"}), 400
        
        price_now_list = Price_Now.query.filter_by(pId=pId).all()
        if not price_now_list:
            return jsonify({"error": "未找到資源"}), 404
        
        # datetime 類型，不能直接丟進 json.dumps()
        results = [
                    {
                        "pId": item.pId,
                        "store": item.store,
                        "updateTime":item.updateTime.isoformat(),
                        "storePrice": float(item.storePrice),
                        "storeDiscount": item.storeDiscount,
                        "storeLink": item.storeLink
                    }for item in price_now_list
                ]
        
        return Response(json.dumps({"results": results}, ensure_ascii=False), mimetype='application/json')

    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        print(f"發生未預期錯誤: {e}")
        return jsonify({'error': '伺服器內部錯誤'}), 500
    
# /productReview/<string:pId>
@goodDetail_bp.route("/productReview/<string:pId>", methods=["GET"])
def get_product_review(pId):
    try:
        if not pId or not isinstance(pId, str):
            return jsonify({"error": "請求參數錯誤"}), 400

        get_review_list = Good_Review.query.filter_by(pId=pId).all()

        if not get_review_list:
            return jsonify({"error": "未找到資源"}), 404
        
        # The date needs to be converted into date format.
        results = [
                    {
                        "pId": item.pId,
                        "userName": item.userName,
                        "date": item.date.isoformat() if item.date else None,
                        "rating": item.rating,
                        "reviewText": item.reviewText
                    }
                    for item in get_review_list
                ]
        return Response(json.dumps({"results": results}, ensure_ascii=False), mimetype='application/json')

    except SQLAlchemyError as e:
        return jsonify({str(e)}), 500
    except Exception as e:
        print(f"發生未預期錯誤: {e}")
        return jsonify({'error': '伺服器內部錯誤'}), 500
    
# /click/<string:pId>
@goodDetail_bp.route("/click/<string:pId>", methods=["POST"]) 
def click(pId):

    try:
        if not pId or not isinstance(pId, str): 
            return jsonify({"error": "請求參數錯誤"}), 400

        # 更新點擊次數
        cache_key = f"click_times:{pId}"
        new_click_times = cache.incr(cache_key)

        return jsonify({
            "message": "點擊次數已累積",
            "new_click_times": int(new_click_times) 
        }), 200
    except Exception as e:
        print(f"發生未預期錯誤: {e}")
        return jsonify({'error': '伺服器內部錯誤'}), 500

@goodDetail_bp.route("/track/id", methods=["POST"])
def track_id():
    try:
        
        data = request.get_json()
        cId = data.get('cId')
        pId = data.get('pId')

        # 驗證參數是否齊全
        if not cId or not pId:
            return jsonify({'error': '請求參數錯誤'}), 400

        # 查詢是否已關注
        favorite = Client_Favorites.query.filter_by(cId=cId, pId=pId).first()

        # 有關注，status = 1
        if favorite:
            return jsonify({
                'cId': cId,
                'pId': pId,
                'status': 1
            }), 200
        else:
            return jsonify({
                'cId': cId,
                'pId': pId,
                'status': 0
            }), 200
        
    except SQLAlchemyError as e:
        return jsonify({str(e)}), 500
    except Exception as e:
        print(f"發生未預期錯誤: {e}")
        return jsonify({'error': '伺服器內部錯誤'}), 500
    
@goodDetail_bp.route("/track", methods=["POST"])
def toggle_track_status():
    try:
        data = request.get_json()
        cId = data.get('cId')
        pId = data.get('pId')
        print(cId + " " + pId)
        if not cId or not pId or not isinstance(pId, str) or not isinstance(cId, str):
            return jsonify({'error': '請求參數錯誤'}), 400

        favorite = db.session.get(Client_Favorites, {'cId': cId, 'pId': pId})

        action_taken = False

        if favorite:
            db.session.delete(favorite)
            new_status = 0
            message = "已取消追蹤"
            action_taken = True
        else:
            product_exists = Product.query.filter_by(pId=pId).first()
            if not product_exists:
                return jsonify({'error': f'無法追蹤，商品 ID {pId} 不存在'}), 404
            add_favorite = Client_Favorites(cId=cId, pId=pId)
            db.session.add(add_favorite)
            new_status = 1
            message = "已加入追蹤"
            action_taken = True

        if action_taken:
            db.session.commit()

        return jsonify({
            'message': message,
            'cId': cId,
            'pId': pId,
            'status': new_status
        }), 200
    except SQLAlchemyError as e:
        print(f"!!! SQLAlchemy Error Details: {e}")
        db.session.rollback()
        return jsonify({'error': f'資料庫操作錯誤: {str(e)}'}), 500
    except Exception as e:
        db.session.rollback()
        print(f"追蹤狀態切換時發生未預期錯誤: {e}")
        return jsonify({'error': '伺服器內部錯誤'}), 500