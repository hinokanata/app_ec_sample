from flask import Flask, render_template, request, redirect, url_for, session
import db
import string
import random
from datetime import timedelta
from werkzeug.utils import secure_filename
import os
import mail

app = Flask(__name__)
app.secret_key = ''.join(random.choices(string.ascii_letters, k=256))
app.config['UPLOAD_FOLDER'] = 'static/uploads'
UPLOAD_FOLDER = 'C://Users/hino/Desktop/Python/app_ec_sample/static/img'


@app.route('/', methods=['GET'])
def index():
    msg = request.args.get('msg')

    if msg is None:
        return render_template('index.html')
    else:
        return render_template('index.html', msg=msg)


@app.route('/login', methods=['POST'])
def login():
    user_name = request.form.get('username')
    password = request.form.get('password')

    if db.login(user_name, password):
        session['user'] = True
        session.permanent = True
        app.permanent_session_lifetime = timedelta(hours=1)
        return redirect(url_for('mypage'))
    else:
        error = 'ログインに失敗しました。'
        input_data = {
            'user_name': user_name,
            'password': password
        }
        return render_template('index.html', error=error, data=input_data)
    
@app.route('/cus', methods=['POST'])
def cus():
    user_name = request.form.get('username')
    password = request.form.get('password')

    if db.login(user_name, password):
        session['user'] = True
        session.permanent = True
        app.permanent_session_lifetime = timedelta(hours=1)
        return redirect(url_for('customer_list'))
    else:
        error = 'ログインに失敗しました。'
        input_data = {
            'user_name': user_name,
            'password': password
        }
        return render_template('index.html', error=error, data=input_data)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))


@app.route('/mypage', methods=['GET'])
def mypage():
    if 'user' in session:
        return render_template('mypage.html')
    else:
        return redirect(url_for('index'))


@app.route('/register')
def register_form():
    return render_template('register.html')


@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/buy')
def buy():
    return render_template('buy.html')

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

@app.route('/customer_list', methods=['GET'])
def customer_list():
    return render_template('customer_list.html')


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'cart' not in session:
        session['cart'] = []

    product = {
        'title': request.form.get('product_name'),
        'size': request.form.get('product_size'),
        'pages': request.form.get('product_pages')
    }

    session['cart'].append(product)

    return redirect(url_for('view_cart'))

@app.route('/purchase', methods=['POST'])
def purchase():
    return redirect(url_for('buyend'))

@app.route('/buyend')
def buyend():
    return render_template('buyend.html')

@app.route('/cart')
def view_cart():
    if 'cart' in session:
        cart_items = session['cart']
        cart_items_with_index = enumerate(cart_items) 
    else:
        cart_items = []
        cart_items_with_index = []

    return render_template('cart.html', cart_items=cart_items_with_index)


@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    if 'cart' in session and 'product_index' in request.form:
        product_index = int(request.form['product_index'])
        if 0 <= product_index < len(session['cart']):
            del session['cart'][product_index]

    return redirect(url_for('view_cart'))

@app.route('/register_exee', methods=['POST'])
def register_exee():
    title = request.form.get('title')
    author = request.form.get('author')
    publisher = request.form.get('publisher')
    pages = request.form.get('pages')

    db.insert_book(title, author, publisher, pages)  

    return redirect(url_for('list_admin'))  



@app.route('/list_products', methods=['GET'])
def list_products():
    keyword = request.args.get('keyword', '')  

    rows = db.select_all_books()
    if keyword:
        filtered_books = []
        for book in rows:
            if keyword in book[0]:  
                filtered_books.append(book)
        return render_template('list_products.html', books=filtered_books, keyword=keyword)
    else:
        return render_template('list_products.html', books=rows)


@app.route('/list_admin', methods=['GET'])
def list_admin():
    keyword = request.args.get('keyword', '')  

    rows = db.select_all_books()
    if keyword:
        filtered_books = []
        for book in rows:
            if keyword in book[0]:  
                filtered_books.append(book)
        return render_template('list_admin.html', books=filtered_books, keyword=keyword)
    else:
        return render_template('list_admin.html', books=rows)


@app.route('/uploads', methods=['POST'])
def uploads():
    if 'file' not in request.files:
        return redirect(url_for('view_cart'))

    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('view_cart'))

    name = secure_filename(file.filename)

    file.save(os.path.join(UPLOAD_FOLDER, name))

    return render_template('customer_list.html', name='images/' + name)

@app.route('/remove_product', methods=['POST'])
def remove_product():
    if 'user' not in session:
        return redirect(url_for('index'))

    product_id = request.form.get('product_id')

    print("Received Product ID:", product_id)  

    if product_id is not None:
        try:
            product_id = int(product_id) 
            print("Product ID to be deleted:", product_id)
            db.remove_product(product_id)  
            print("Product deleted successfully!")
        except (ValueError, TypeError):
            print("Invalid product_id:", product_id)
        except Exception as e:
            print("Error deleting product:", str(e))

    return redirect(url_for('list_admin'))

if __name__ == '__main__':
    app.run(debug=True)
