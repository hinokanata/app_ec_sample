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

@app.route('/login', methods=['POST'])
def login():
    user_name = request.form.get('username')
    password = request.form.get('password')
    
    if db.login(user_name, password):
        session['user'] = True 
        session.permanent = True
        app.permanent_session_lifetime = timedelta(hours=1)
        return redirect(url_for('customer'))
    else :    
        error = 'ログインに失敗しました。'
        input_data ={
            'user_name' : user_name,
            'password' : password
        }
        return render_template('index.html', error=error, data=input_data)
    
@app.route('/adminlogin', methods=['POST'])
def adminlogin():
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
        return render_template('admin.html', error=error, data=input_data)

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

@app.route('/admin')
def admin():
    return render_template('admin.html')

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

@app.route('/add_product')
def add_product():
    return render_template('add_product.html')

@app.route('/customer')
def customer():
    return render_template('customer.html')

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

@app.route('/register_exee', methods=['POST'])
def register_exee():
    title = request.form.get('title')
    author = request.form.get('author')
    publisher = request.form.get('publisher')
    pages = request.form.get('pages')
    
    db.insert_book(title, author, publisher, pages)
    
    book_list = db.select_all_books()
    
    return render_template('list_products.html','list.html', books=book_list)

@app.route('/list')
def list():
    book_list = db.select_all_books()
    return render_template('list.html', books=book_list)

@app.route('/list_products')
def list_products():
    book_list = db.select_all_books()
    return render_template('list_products.html', books=book_list)

@app.route('/delete_product/<int:book_id>', methods=['POST'])
def delete_product(book_id):
    db.delete_book(book_id)
    return redirect(url_for('list_products'))


if __name__ == '__main__':
    app.run(debug=True)