import os
from flask import Flask, render_template, request, redirect
from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.sql import func
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, EqualTo
from forms import RegisterForm
from flask import session 

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///myblog.db'
db = SQLAlchemy(app)

class BlogPost(db.Model):
    __tablename__ = 'blog_post'#테이블 이름
    id = db.Column(db.Integer, primary_key=True) #id를 프라이머리키로 설정
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(20), nullable=False, default='N/A')
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Fcuser(db.Model): 
    __tablename__ = 'fcuser'   #테이블 이름 
    id = db.Column(db.Integer, primary_key = True)   
    password = db.Column(db.String(64))     #패스워드를 받아올 문자열길이 
    userid = db.Column(db.String(32))       #이하 위와 동일
    username = db.Column(db.String(8))

    # def __repr__(self):
    #     return 'Blog post ' + str(self.id)

@app.route('/sign_up', methods=['GET','POST'])  #겟, 포스트 메소드 둘다 사용
def register():   #get 요청 단순히 페이지 표시 post요청 회원가입-등록을 눌렀을때 정보 가져오는것
    form = RegisterForm()
    if form.validate_on_submit(): # POST검사의 유효성검사가 정상적으로 되었는지 확인할 수 있다. 입력 안한것들이 있는지 확인됨.
        #비밀번호 = 비밀번호 확인 -> EqulaTo
    
        fcuser = Fcuser()  #models.py에 있는 Fcuser 
        fcuser.userid = form.data.get('userid')
        fcuser.username = form.data.get('username')
        fcuser.password = form.data.get('password')
            
        print(fcuser.userid,fcuser.password)  #회원가입 요청시 콘솔창에 ID만 출력 (확인용, 딱히 필요없음)
        db.session.add(fcuser)  # id, name 변수에 넣은 회원정보 DB에 저장
        db.session.commit()  #커밋
        
        return "가입 완료" #post요청일시는 '/'주소로 이동. (회원가입 완료시 화면이동)
            
    return render_template('register.html', form=form)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/myblog', methods=['GET', 'POST'])
def posts():

    if request.method == 'POST':
        post_title = request.form['title']
        post_content = request.form['content']
        post_author = request.form['author']
        new_post = BlogPost(title=post_title, content=post_content, author=post_author)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/myblog')
    else:
        all_posts = BlogPost.query.order_by(BlogPost.date_posted).all()
        return render_template('myblog.html', posts=all_posts)

@app.route('/myblog/delete/<int:id>')
def delete(id):
    post = BlogPost.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return redirect('/myblog')

@app.route('/myblog/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    
    post = BlogPost.query.get_or_404(id)

    if request.method == 'POST':
        post.title = request.form['title']
        post.author = request.form['author']
        post.content = request.form['content']
        db.session.commit()
        return redirect('/myblog')
    else:
        return render_template('edit.html', post=post)

@app.route('/myblog/new', methods=['GET', 'POST'])
def new_post():
    if request.method == 'POST':
        post.title = request.form['title']
        post.author = request.form['author']
        post.content = request.form['content']
        new_post = BlogPost(title=post_title, content=post_content, author=post_author)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/posts')
    else:
        return render_template('new_post.html')

@app.route('/logout',methods=['GET'])
def logout():
    session.pop('userid',None)
    return redirect('/')

if __name__ == "__main__":
    basedir = os.path.abspath(os.path.dirname(__file__)) #db파일을 절대경로로 생성
    dbfile = os.path.join(basedir, 'myblog.db')#db파일을 절대경로로 생성

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + dbfile   
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True 
#사용자 요청의 끝마다 커밋(데이터베이스에 저장,수정,삭제등의 동작을 쌓아놨던 것들의 실행명령)을 한다.
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
#수정사항에 대한 track을 하지 않는다. True로 한다면 warning 메시지유발
    app.config['SECRET_KEY'] = 'wcsfeufhwiquehfdx'

    db.create_all()  #db 생성

    app.run(host='127.0.0.1', port=5000, debug=True) 
     #포트번호는 기본 5000, 개발단계에서는 debug는 True
