import os, psycopg2, string, random, hashlib, sqlite3


connection = psycopg2.connect(user='postgres',
                              password='0818',
                              host='localhost',
                              database='postgres')


def get_salt():
    charset = string.ascii_letters + string.digits
    
    salt = ''.join(random.choices(charset, k=30))
    return salt

def get_hash(password, salt):
    b_pw = bytes(password, 'utf-8')
    b_salt = bytes(salt, 'utf-8')
    hashed_password = hashlib.pbkdf2_hmac('sha256', b_pw, b_salt, 1000).hex()
    return hashed_password

def insert_user(user_name, password):
    sql = 'INSERT INTO user_sample VALUES(default, %s, %s, %s)'
    
    salt = get_salt()
    hashed_password = get_hash(password, salt)
    
    try :
        connection = get_connection()
        cursor = connection.cursor()
        
        cursor.execute(sql, (user_name, hashed_password, salt))
        count = cursor.rowcount 
        connection.commit()
    
    except psycopg2.DatabaseError: 
        count = 0
        
    finally :
        cursor.close()
        connection.close()
        
    return count

def login(user_name, password):
    sql = 'SELECT hashed_password, salt FROM user_sample WHERE name = %s'
    flg = False
    
    try :
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (user_name, ))
        user = cursor.fetchone()
        
        if user != None:
            salt = user[1]
            
            hashed_password = get_hash(password, salt)
            
            if hashed_password == user[0]:
                flg = True
                
    except psycopg2.DatabaseError:
        flg = False
    finally :
        cursor.close()
        connection.close()
        
    return flg


def get_connection():
	url = os.environ['DATABASE_URL']
	connection = psycopg2.connect(url)
	return connection

def select_all_books():
    connection = get_connection()
    cursor = connection.cursor()
    
    sql = 'SELECT title, author, publisher, pages FROM books_sample'
    
    cursor.execute(sql)
    rows = cursor.fetchall()
    
    cursor.close()
    connection.close()
    return rows
    
def insert_book(title, author, publisher, pages):
    connection = get_connection()
    cursor = connection.cursor()
    sql = 'INSERT INTO books_sample VALUES (default, %s, %s, %s, %s)'
    
    cursor.execute(sql, (title, author, publisher, pages))
    connection.commit()
    cursor.close()
    connection.close()
    
def remove_product(product_id):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        sql = 'DELETE FROM books_sample WHERE id = %s'
        cursor.execute(sql, (product_id,))
        connection.commit()
        print("Product deleted successfully!")
    except Exception as e:
        print("Error deleting product:", str(e))

    cursor.close()
    connection.close()
