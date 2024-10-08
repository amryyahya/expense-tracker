from flask import Flask, request, jsonify
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app import app, users
from app.utils import filter_by_date, filter_by_amount, build_pipeline
from app.default_categories import DEFAULT_CATEGORIES
import uuid

@app.route('/check-email', methods=['POST'])
def checkEmail():
    try:
        email = request.get_json().get('email')
        if users.count_documents({"email": email}) > 0:
            return jsonify({"exist": True}), 200
        return jsonify({"exist": False}), 200
    except Exception as e:
        print(str(e))
    
@app.route('/check-username', methods=['POST'])
def checkUsername():
    try:
        username = request.get_json().get('username')
        if users.count_documents({"username": username}) > 0:
            return jsonify({"exist": True}), 200
        return jsonify({"exist": False}), 200
    except Exception as e:
        print(str(e))

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    displayName = data.get('displayName')
    password = data.get('password')
    if not (username or email) or not password:
        return jsonify({"msg": "Username/Email and password are required"}), 400
    userExist = users.count_documents({"username": username} if username else {"email": email}) > 0
    if userExist:
        return jsonify({"msg": "user has already exist"}), 400
    user = {
        "username":username,
        "email":email,
        "displayName": displayName,
        "password": generate_password_hash(password),
        "categories":DEFAULT_CATEGORIES,
        "expenses":[],
        "blockedToken":[],
        "createdDate": datetime.now().isoformat()
    }
    users.insert_one(user)
    return jsonify({"msg": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    if not (username or email) or not password:
        return jsonify({"msg": "Username/email and password are required"}), 400
    user = users.find_one(
        {"username": username} if username else {"email": email},
        {"_id": 0, "password": 1}
    )
    if not user:
        return jsonify({"msg": "Invalid user"}), 401
    if not check_password_hash(user["password"],password):
        return jsonify({"msg": "invalid password"}), 401
    access_token = create_access_token(identity=username)
    refresh_token = create_refresh_token(identity=username)
    return jsonify({
        'access_token':access_token,
        'refresh_token':refresh_token
    }), 200

@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    return jsonify(access_token=new_access_token), 200

################ EXPENSE ROUTE ################################################################
@app.route('/expenses', methods=['GET'])
@jwt_required()
def getExpenses():
    current_user = get_jwt_identity()
    # Pagination
    page = int(request.args.get('page',1))
    limit = int(request.args.get('limit',10))
    skip = (page - 1) * limit
    match_conditions = {}
    # Date range filtering
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    if start_date or end_date: match_conditions['expenses.date'] = filter_by_date(start_date, end_date)
    # Amount range filtering
    min_amount = request.args.get('min_amount')
    max_amount = request.args.get('max_amount')
    if min_amount or max_amount: match_conditions['expenses.amount'] = filter_by_amount(min_amount, max_amount)
    # Category filtering
    categories = request.args.getlist('category') 
    if categories:
        match_conditions['expenses.category'] = {'$in': categories}
    # Sorting
    sort_by = request.args.get('sort_by',"date")
    order = request.args.get('order', 'desc')
    sort_order = 1 if order == 'asc' else -1
    # Querying
    pipeline = build_pipeline(current_user, "expenses", match_conditions, f"expenses.{sort_by}", sort_order, skip, limit) 
    results = users.aggregate(pipeline)
    print(pipeline)
    expenses_list = [result['expenses'] for result in results]
    return jsonify({"expenses": expenses_list}),200

@app.route('/expenses', methods=['POST'])
@jwt_required()
def addExpense():
    current_user = get_jwt_identity()
    data = request.get_json()
    amount = data.get('amount')
    category = data.get('category')
    description = data.get('description')
    date = data.get('date',datetime.now().isoformat())
    newExpense = {
        "_id": str(uuid.uuid4()),  
        "amount": amount,
        "category": category,
        "description": description,
        "date": date 
    }
    users.update_one(
        { "username": current_user },  
        { "$push": { "expenses": newExpense } }
    )
    return jsonify(status="expense record added"), 200

@app.route('/expenses', methods=['DELETE'])
@jwt_required()
def deleteExpense():
    current_user = get_jwt_identity()
    data = request.get_json()
    expenseId = data.get('_id')
    users.update_one(
        { "username": current_user},
        { "$pull": { "expenses": { "_id": expenseId}}}
    )
    return jsonify(status="expense record deleted"), 200

################ CATEGORY ROUTE ################################################################
@app.route('/categories', methods=['GET'])
@jwt_required()
def getAllCategories():
    current_user = get_jwt_identity()
    user = users.find_one({"username":current_user})
    return jsonify({"categories": user.get("categories")}),200

@app.route('/categories', methods=['POST'])
@jwt_required()
def addCategory():
    current_user = get_jwt_identity()
    data = request.get_json()
    categoryName = data.get('name')
    newCategory = {
        "name": categoryName,
        "date": datetime.now().isoformat()
    }
    users.update_one(
        { "username": current_user },  
        { "$push": { "categories": newCategory } }
    )
    return jsonify(status="new category added"), 200

@app.route('/categories', methods=['DELETE'])
@jwt_required()
def deleteCategory():
    current_user = get_jwt_identity()
    data = request.get_json()
    categoryName = data.get('name')
    users.update_one(
        { "username": current_user},
        { "$pull": { "categories": { "name": categoryName}}}
    )
    return jsonify(status="a category deleted"), 200