from flask import Flask, render_template, request, redirect, url_for, session
import db, string, random, sqlite3
from datetime import timedelta
import mail

app = Flask(__name__)
app.secret_key = ''.join(random.choices(string.ascii_letters, k=256))
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

@app.route('/', methods=['GET'])
def index():
    msg =  request.args.get('msg')

    if msg == None:
        return render_template('index.html')
    else :
        return render_template('index.html', msg=msg)

@app.route('/', methods=['POST'])
def login():
    user_name = request.form.get('username')
    password = request.form.get('password')
    
    if db.login(user_name, password):
        session['user'] = True 
        session.permanent = True
        app.permanent_session_lifetime = timedelta(hours=1)
        return redirect(url_for('mypage'))
    else :    
        error = 'ログインに失敗しました。'
        input_data ={
            'user_name' : user_name,
            'password' : password
        }
        return render_template('index.html', error=error, data=input_data)
    
@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect(url_for('index'))
    
@app.route('/mypage', methods=['GET'])
def mypage():
    if 'user' in session:
        return render_template('mypage.html')
    else :
        return redirect(url_for('index'))
    
@app.route('/register')
def register_form():
    return render_template('register.html')

@app.route('/register_exe', methods=['POST'])
def register_exe():
    user_name = request.form.get('username')
    password = request.form.get('password')
    
    if user_name == '':
        error = 'ユーザー名が未入力です。'
        return render_template('register.html', error=error)
    if password == '':
        error = 'パスワードが未入力です。'
        return render_template('register.html', error=error)
    
    count = db.insert_user(user_name, password)
    
    if count == 1:
        msg = '登録が完了しました。'
        return redirect(url_for('index', msg=msg))
    else:
        error = '登録に失敗しました。'
        return render_template('register.html', error=error)
    
@app.route('/indexmail')
def indexmail():
    return render_template('indexmail.html')

@app.route('/send', methods=['POST'])
def send():
    to = request.form.get('to')
    subject = request.form.get('subject')
    body = request.form.get('body')
    
    mail.send_mail(to, subject, body)
    
    return redirect(url_for('navigateSend'))

@app.route('/send', methods=['GET'])
def navigateSend():
    return render_template('send.html')

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = request.form['product_id']
    if 'cart' not in session:
        session['cart'] = []
    session['cart'].append(product_id)
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    if 'cart' not in session:
        session['cart'] = []
    cart_items = session['cart']
    return render_template('cart.html', cart_items=cart_items)

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    product_id = request.form['product_id']
    if 'cart' in session and product_id in session['cart']:
        session['cart'].remove(product_id)
    return redirect(url_for('cart'))

@app.route('/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        image = request.form['image']
        
        # データベースに商品を追加
        conn = sqlite3.connect('products.db')
        c = conn.cursor()
        c.execute('INSERT INTO products (name, description, image) VALUES (?, ?, ?)',
                  (name, description, image))
        conn.commit()
        conn.close()
        
        return redirect(url_for('list_products'))
    
    return render_template('add_product.html')

# 商品一覧表示のルート
@app.route('/list_products')
def list_products():
    # データベースから商品を取得
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    c.execute('SELECT * FROM products')
    products = c.fetchall()
    conn.close()
    
    return render_template('list_products.html', products=products)

if __name__ == '__main__':
    app.run(debug=True)