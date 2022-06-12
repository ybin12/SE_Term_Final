import os
from datetime import datetime
from distutils.log import info
from re import S
from tokenize import String

from flask import *
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///SE_term_project.sqlite3'
app.config['SECRET_KEY'] = "0000"

db = SQLAlchemy(app)

#사용자 계정 모델
class accounts(db.Model):
    id = db.Column(db.Integer, primary_key = True, unique = True, autoincrement = True)
    a_id = db.Column(db.String(20))
    a_pw = db.Column(db.String(20))
    
    def __init__(self, id, pw):
        self.a_id = id
        self.a_pw = pw
        
#상품 정보 모델
class products(db.Model):
    id = db.Column(db.Integer, primary_key = True, unique = True, autoincrement = True)
    p_id = db.Column(db.String(20))
    p_info = db.Column(db.String(500))
    p_key = db.Column(db.String(20))
    p_time = db.Column(db.String(100))
    p_img = db.Column(db.String(500))
    p_sold = db.Column(db.String(20))
    p_price = db.Column(db.String(50))
    
    def __init__(self, id, info, key, time, img, sold, price):
        self.p_id = id
        self.p_info = info
        self.p_key = key
        self.p_time = time
        self.p_img = img
        self.p_sold = sold
        self.p_price = price

#팔로우 정보 모델        
class follows(db.Model):
    id = id = db.Column(db.Integer, primary_key = True, unique = True, autoincrement = True)
    f_er = db.Column(db.String(20))
    f_ee = db.Column(db.String(20))
    
    def __init__(self, er, ee):
        self.f_er = er
        self.f_ee = ee

#메인페이지        
@app.route('/', methods = ['POST', 'GET'])
def first_page():
    return render_template("first_page.html", product_list = products.query.all())
    
#로그인
@app.route('/login',methods = ['POST', 'GET'])
def login():
    if request.method == "POST":
        if not request.form['a_id']:
            flash("아이디를 입력해주세요")
            return render_template("login.html")
        elif not request.form['a_pw']:
            flash("비밀번호를 입력해주세요")
            return render_template("login.html")
        
        check_id = accounts.query.filter_by(a_id = request.form['a_id']).first()
        if check_id:
            check_pw = accounts.query.filter_by(a_id = request.form['a_id'], a_pw = request.form['a_pw']).first()
            if check_pw:
                session['id'] = request.form['a_id']
                
                flash("안녕하세요 "+session['id']+" 님")
                return redirect(url_for('first_page'))
            else:
                flash("잘못된 비밀번호입니다")
                return render_template("login.html")
        else:
            flash("없는 회원입니다")
            return render_template("login.html")
        
    else:
        return render_template("login.html")
    
#로그아웃
@app.route('/logout')
def logout():
    session.pop('id',None)
    flash("로그아웃 되었습니다")
    return redirect(url_for('first_page'))
    
#회원가입
@app.route('/signup', methods = ['POST', 'GET'])
def signup():
    if request.method == "POST":
        if not request.form['a_id']:
            flash("아이디를 입력해주세요")
            return render_template("signup.html")
        elif not request.form['a_pw']:
            flash("비밀번호를 입력해주세요")
            return render_template("signup.html")
        
        check_id = accounts.query.filter_by(a_id = request.form['a_id']).first()
        if check_id:
            flash("이미 가입된 아이디입니다")
            return render_template("signup.html")
        
        signup = accounts(request.form['a_id'], request.form['a_pw'])
        db.session.add(signup)
        db.session.commit()
        
        flash("회원가입이 완료되었습니다")
        return redirect(url_for('login'))
    else:
        return render_template("signup.html")
    
#상품 정보 글쓰기
@app.route('/write',methods = ['POST', 'GET'])
def write():
    if 'id' not in session:
        flash("로그인하지 않으면 등록이 불가능합니다")
        return redirect(url_for('first_page'))
    elif request.method == "POST":
        image = request.files['p_img']
        image_fn = secure_filename(image.filename)
        if not request.form['p_info']:
            flash("상품정보를 입력해주세요")
            return render_template("write.html")
        elif not request.form['p_key']:
            flash("키워드를 입력해주세요")
            return render_template("write.html")
        elif not request.form['p_price']:
            flash("가격을 입력해주세요")
            return render_template("write.html")
        elif not image_fn:
            flash("사진을 첨부해주세요")
            return render_template("write.html")
        while os.path.isfile(image_fn):
            image_fn = "(1)" + image_fn
        image.save("static/" + image_fn)
        write = products(session['id'], request.form['p_info'], request.form['p_key'], datetime.now(), image_fn, "판매중", request.form['p_price'])
        db.session.add(write)
        db.session.commit()
        
        flash("상품정보 등록이 완료되었습니다")
        return redirect(url_for('first_page'))
    else:
        return render_template("write.html")

#상품 정보 페이지    
@app.route('/product_page/<input_id>')
def product_page(input_id):
    product = products.query.filter_by(id = input_id).first()
    return render_template("product.html", products = product)

#상품 정보 수정
@app.route('/modify/<input_id>',methods = ['POST', 'GET'])
def modify(input_id):
    product = products.query.filter_by(id = input_id).first()
    if request.method == "POST" and session['id'] == product.p_id:
        if not request.form['p_info']:
            flash("상품정보를 입력해주세요")
            return render_template("modify.html")
        elif not request.form['p_key']:
            flash("키워드를 입력해주세요")
            return render_template("modify.html")
        elif not request.form['p_price']:
            flash("가격을 입력해주세요")
            return render_template("modify.html")

        product.p_info = request.form['p_info']
        product.p_key = request.form['p_key']
        product.p_price = request.form['p_price']
        product.p_time = datetime.now()
        db.session.commit()
        
        flash("상품정보 수정이 완료되었습니다")
        return redirect(url_for('product_page', input_id = input_id))
    elif 'id' not in session:
        flash("로그인하지 않으면 수정이 불가능합니다")
        return redirect(url_for('product_page', input_id = input_id))
    elif session['id'] != product.p_id:
        flash("다른 회원의 상품 정보는 수정할 수 없습니다")
        return redirect(url_for('product_page', input_id = input_id))
    
    else:
        return render_template("modify.html", products = product)

#상품 정보 삭제    
@app.route('/delete/<input_id>')
def delete(input_id):
    product = products.query.filter_by(id = input_id).first()
    if 'id' not in session:
        flash("로그인하지 않으면 삭제가 불가능합니다")
        return redirect(url_for('product_page', input_id = input_id))
    elif session['id'] != product.p_id:
        flash("다른 회원의 상품 정보는 삭제할 수 없습니다")
        return redirect(url_for('product_page', input_id = input_id))
    else:
        os.remove("static/"+product.p_img)
        db.session.delete(product)
        db.session.commit()
        flash("삭제가 완료되었습니다")
        return redirect(url_for('first_page'))

#상품 판매완료 처리    
@app.route('/sold/<input_id>')
def sold(input_id):
    product = products.query.filter_by(id = input_id).first()
    if 'id' not in session:
        flash("로그인하지 않으면 판매완료 처리가 불가능합니다")
        return redirect(url_for('product_page', input_id = input_id))
    elif session['id'] != product.p_id:
        flash("다른 회원의 상품은 판매완료 처리할 수 없습니다")
        return redirect(url_for('product_page', input_id = input_id))
    elif product.p_sold == "판매완료":
        product.p_sold = "판매중"
        db.session.commit()
        flash("판매완료 처리를 취소하었습니다")
        return redirect(url_for('product_page', input_id = input_id))
    else:
        product.p_sold = "판매완료"
        db.session.commit()
        flash("판매완료 처리가 완료되었습니다")
        return redirect(url_for('product_page', input_id = input_id))

#상품 키워드 검색    
@app.route('/search_key', methods = ['POST', 'GET'])
def search_key():
    product = products.query.filter_by(p_key = request.form['key']).all()
    return render_template("search_key.html", product_list = product, result = request.form['key']) 

#다른 유저 팔로우
@app.route('/follow/<input_id>')
def follow(input_id):
    if 'id' not in session:
        flash("팔로우를 위해 로그인을 해주세요")
        return redirect(url_for('login'))
    else:
        follow = follows.query.filter_by(f_er = session['id'], f_ee = input_id).first()
        if follow:
            flash("이미 팔로우한 회원입니다")
            return redirect(url_for('first_page'))
        elif session['id'] == input_id:
            flash("자기 자신을 팔로우 할 수 없습니다")
            return redirect(url_for('first_page'))
        else:
            do_follow = follows(session['id'], input_id)
            db.session.add(do_follow)
            db.session.commit()
            flash(input_id + " 유저를 팔로우 하였습니다")
            return redirect(url_for('first_page'))

#팔로우한 유저 목록
@app.route('/follower_page')
def follower_page():
    if 'id' not in session:
        flash("팔로우 목록을 확인하려면 로그인이 필요합니다")
        return redirect(url_for('login'))
    else:        
        follow = follows.query.filter_by(f_er = session['id']).all()
        return render_template("follower_page.html", follow_list = follow, user = session['id'])

#팔로우한 유저의 상품 목록    
@app.route('/search_f_ee/<input_id>')
def search_f_ee(input_id):
    product = products.query.filter_by(p_id = input_id).all()
    return render_template("search_f_ee.html",product_list = product, user = input_id)

#팔로우한 유저 언팔로우
@app.route('/delete_f_ee/<input_id>')
def delete_f_ee(input_id):
    follow = follows.query.filter_by(f_er = session['id'], f_ee = input_id).first()
    db.session.delete(follow)
    db.session.commit()
    flash("언팔로우가 완료되었습니다")
    return redirect(url_for('follower_page'))

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)