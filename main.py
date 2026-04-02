import random
from flask import Flask, render_template, request, redirect, url_for, session
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.secret_key = 'cset170secretkey'

conn_str = 'mysql://root:cset155@localhost/bankdb'
engine = create_engine(conn_str, echo=True)
conn = engine.connect()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['POST'])
def register_post():
    try:
        conn.execute(
            text('INSERT INTO users (fName, lName, SSN, address, phoneNum, pw, status) VALUES (:fName, :lName, :SSN, :address, :phoneNum, :pw, :status)'),
            {
                "fName": request.form["fName"],
                "lName": request.form["lName"],
                "SSN": request.form["SSN"],
                "address": request.form["address"],
                "phoneNum": request.form["phoneNum"],
                "pw": request.form["pw"],
                "status": "pending"
            }
        )
        conn.commit()
        return render_template('index.html', success="Account created! Awaiting admin approval.")
    except IntegrityError:
        return render_template('index.html', error="An account with that SSN already exists.")

@app.route('/login', methods=['POST'])
def login_post():
    ssn = request.form["SSN"]
    pw = request.form["pw"]
    user = conn.execute(
        text("SELECT * FROM users WHERE SSN = :SSN AND pw = :pw"),
        {"SSN": ssn, "pw": pw}
    ).mappings().fetchone()
    if user:
        if user['status'] == 'pending':
            return render_template('index.html', login_error="Your account is pending admin approval.")
        if user['isAdmin'] == 1:
            return redirect(url_for('admin'))
        session['ssn'] = user['SSN']
        session['acc_num'] = user['accNum']
        return redirect(url_for('balance'))
    else:
        return render_template('index.html', login_error="Invalid SSN or password.")

@app.route('/admin')
def admin():
    pending_users = conn.execute(
        text("SELECT * FROM users WHERE status = 'pending'")
    ).mappings().fetchall()
    return render_template('admin.html', pending_users=pending_users)

@app.route('/admin/approve/<ssn>', methods=['POST'])
def approve_user(ssn):
    while True:
        acc_num = str(random.randint(1000000000, 9999999999))
        existing = conn.execute(
            text("SELECT 1 FROM users WHERE accNum = :accNum"),
            {"accNum": acc_num}
        ).fetchone()
        if not existing:
            break
    conn.execute(
        text("UPDATE users SET status = 'approved', accNum = :accNum, balance = 0 WHERE SSN = :SSN"),
        {"accNum": acc_num, "SSN": ssn}
    )
    conn.commit()
    return redirect(url_for('admin'))

@app.route('/admin/deny/<ssn>', methods=['POST'])
def deny_user(ssn):
    conn.execute(
        text("DELETE FROM users WHERE SSN = :SSN"),
        {"SSN": ssn}
    )
    conn.commit()
    return redirect(url_for('admin'))

@app.route('/balance')
def balance():
    if 'ssn' not in session:
        return redirect(url_for('index'))
    user = conn.execute(
        text("SELECT * FROM users WHERE SSN = :SSN"),
        {"SSN": session['ssn']}
    ).mappings().fetchone()
    return render_template('balance.html', user=user)

@app.route('/deposit', methods=['POST'])
def deposit():
    if 'ssn' not in session:
        return redirect(url_for('index'))
    amount = int(request.form['depositAmt'])
    if amount <= 0:
        user = conn.execute(
            text("SELECT * FROM users WHERE SSN = :SSN"),
            {"SSN": session['ssn']}
        ).mappings().fetchone()
        return render_template('balance.html', user=user, error="Amount must be greater than 0.")
    conn.execute(
        text("UPDATE users SET balance = balance + :amount WHERE SSN = :SSN"),
        {"amount": amount, "SSN": session['ssn']}
    )
    conn.commit()
    user = conn.execute(
        text("SELECT * FROM users WHERE SSN = :SSN"),
        {"SSN": session['ssn']}
    ).mappings().fetchone()
    return render_template('balance.html', user=user, success=f"Deposited ${amount} successfully.")

@app.route('/withdraw', methods=['POST'])
def withdraw():
    if 'ssn' not in session:
        return redirect(url_for('index'))
    amount = int(request.form['withdrawAmt'])
    user = conn.execute(
        text("SELECT * FROM users WHERE SSN = :SSN"),
        {"SSN": session['ssn']}
    ).mappings().fetchone()
    if amount <= 0:
        return render_template('balance.html', user=user, error="Amount must be greater than 0.")
    if user['balance'] < amount:
        return render_template('balance.html', user=user, error="Insufficient funds.")
    conn.execute(
        text("UPDATE users SET balance = balance - :amount WHERE SSN = :SSN"),
        {"amount": amount, "SSN": session['ssn']}
    )
    conn.commit()
    user = conn.execute(
        text("SELECT * FROM users WHERE SSN = :SSN"),
        {"SSN": session['ssn']}
    ).mappings().fetchone()
    return render_template('balance.html', user=user, success=f"Withdrew ${amount} successfully.")

@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if 'ssn' not in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        to_acc = request.form['to_acc']
        amount = int(request.form['amount'])
        sender = conn.execute(
            text("SELECT * FROM users WHERE SSN = :SSN"),
            {"SSN": session['ssn']}
        ).mappings().fetchone()
        if amount <= 0:
            return render_template('transfer.html', error="Amount must be greater than 0.")
        if sender['balance'] < amount:
            return render_template('transfer.html', error="Insufficient funds.")
        recipient = conn.execute(
            text("SELECT * FROM users WHERE accNum = :accNum"),
            {"accNum": to_acc}
        ).mappings().fetchone()
        if not recipient:
            return render_template('transfer.html', error="Account number not found.")
        if recipient['accNum'] == sender['accNum']:
            return render_template('transfer.html', error="You cannot transfer to your own account.")
        conn.execute(
            text("UPDATE users SET balance = balance - :amount WHERE SSN = :SSN"),
            {"amount": amount, "SSN": session['ssn']}
        )
        conn.execute(
            text("UPDATE users SET balance = balance + :amount WHERE accNum = :accNum"),
            {"amount": amount, "accNum": to_acc}
        )
        conn.commit()
        return render_template('transfer.html', success=f"Successfully transferred ${amount} to account {to_acc}.")
    return render_template('transfer.html')

if __name__ == '__main__':
    app.run(debug=True)