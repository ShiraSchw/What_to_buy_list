from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import requests  # הוספנו את הספרייה הזאת עבור חיפושי האייקונים

app = Flask(__name__)

# חיבור למסד נתונים עם הגדרה למצב של חוטים שונים
conn = sqlite3.connect('shopping_list.db', check_same_thread=False)
c = conn.cursor()

# יצירת טבלת רשימת קניות אם לא קיימת
c.execute('''CREATE TABLE IF NOT EXISTS shopping_list (item TEXT, quantity INTEGER)''')

# פונקציה לחיפוש אייקון (API)
def search_icon(item_name):
    # URL לאייקונים דרך Iconify API
    url = f"https://api.iconify.design/{item_name}.json"

    # שליחת בקשה ל-API
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        # קבלת ה-URL של האייקון הראשון במערך
        icon_url = data.get('icons', [{}])[0].get('icon', {}).get('src', None)
        return icon_url
    else:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # הוספת מוצר לרשימה
        item = request.form['item']
        quantity = request.form['quantity']

        # קישור למסד הנתונים כדי לשמור את המוצר
        connection = sqlite3.connect('shopping_list.db')
        c = connection.cursor()
        c.execute('INSERT INTO shopping_list (item, quantity) VALUES (?, ?)', (item, quantity))
        connection.commit()
        connection.close()

    # קריאה ממסד הנתונים
    connection = sqlite3.connect('shopping_list.db')
    c = connection.cursor()
    c.execute('SELECT item, quantity FROM shopping_list')
    items = c.fetchall()
    connection.close()

    # שולחים את המידע לתבנית
    return render_template('index.html', items=items, search_icon=search_icon)

@app.route('/add', methods=['POST'])
def add_item():
    item = request.form['item']
    quantity = request.form['quantity']
    c.execute('INSERT INTO shopping_list (item, quantity) VALUES (?, ?)', (item, quantity))
    conn.commit()
    return redirect(url_for('index'))

@app.route('/remove/<item>', methods=['GET'])
def remove_item(item):
    c.execute('DELETE FROM shopping_list WHERE item = ?', (item,))
    conn.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

