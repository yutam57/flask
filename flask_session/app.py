from flask import flash, redirect, render_template, url_for, request, Flask
from flask_login import LoginManager, logout_user, login_required, login_user
import flask_login
import flask
import os
import logging.config

# ログ設定ファイルからログ設定を読み込み
logging.config.fileConfig('logging.conf')
logger = logging.getLogger()
logger.setLevel(21)
 
from DataStore.MySQL import MySQL
dns = {
    'user': 'root',
    'host': 'localhost',
    'password': 'Akasatana2315',
    'database': 'test'
}
db = MySQL(**dns)

app = Flask(__name__)
app.secret_key = os.urandom(24)
users = {'H3044782': {'password': 'Akasatana2315'} , 'hoge': {'password': 'piyo'}}

class User(flask_login.UserMixin):
	pass

# flask-loginを設定
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
	if user_id not in users:
		return

	user = User()
	user.id = user_id
	return user

@login_manager.request_loader
def request_loader(request):
	user_id = request.form.get('username')
	if user_id not in users:
		return

	user = User()
	user.id = user_id

	# DO NOT ever store passwords in plaintext and always compare password
	# hashes using constant-time comparison!
	user.is_authenticated = request.form['password'] == users[user_id]['password']
	return user

# 初期画面
@app.route('/', methods=['GET'])
def form():
	return render_template('login.html')
 
@app.route('/login', methods=['POST'])
def login():
	global user_id
	user_id = flask.request.form['username']
	password = flask.request.form['password']

	if password == users[user_id]['password']:
		user = User()
		user.id = user_id
		login_user(user)
		flash(u'login success','success')
		logger.log(21, '%sさんがログインしました。'%(user_id))
		return redirect(url_for('main'))
	else:
		flash(u'The username or password you entered is incorrect.', 'error')
		return redirect(url_for('form'))

# ログアウト
@app.route('/logout')
def logout():
	logout_user()
	logger.log(21, '%sさんがログアウトしました。'%(user_id))
	return redirect(url_for('form'))

#  ------------------------------------

@app.route('/index')
@login_required
def main():
	search_keyword = request.args.get("search_keyword","")
	props = {'title': 'Step-by-Step Flask - index'}
	if search_keyword:
		stmt = 'SELECT * FROM items where item_id like "%%%s%%" or name like "%%%s%%" or price like "%%%s%%"' %(search_keyword,search_keyword,search_keyword);
		logger.log(21, 'user:%s search_keyword:%s'%(user_id,search_keyword))
	else:
		stmt = 'SELECT * FROM items'
	
	items = db.query(stmt)
	html = render_template('index.html', props=props, items=items)
	return html

@app.errorhandler(404)
def not_found(error):
	return render_template('404.html')

@app.errorhandler(KeyError)
def KeyError(error):
	flash(u'The username or password you entered is incorrect.', 'error')
	return redirect(url_for('form'))

@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('401.html')



if __name__ == "__main__":
	app.run(debug=True)