from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = 'secret'
app.config.update({
   'MAIL_SERVER':'smtp.example.com',
   'MAIL_PORT':587,
   'MAIL_USERNAME':'you@example.com',
   'MAIL_PASSWORD':'yourpass',
   'MAIL_USE_TLS':True
})
mail = Mail(app)

def get_db():
    conn = sqlite3.connect('complaints.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_complaint_details(complaint_id):
    db = get_db()  # Assuming get_db() returns a database connection
    complaint = db.execute(
        '''
        SELECT complaints.id, users.email, categories.name AS category,
               description, status, created_at, updated_at
        FROM complaints
        JOIN users ON complaints.user_id = users.id
        JOIN categories ON complaints.category_id = categories.id
        WHERE complaints.id = ?
        ''', (complaint_id,)
    ).fetchone()
    return complaint


@app.route('/', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        # Process the form submission
        email = request.form['email']
        category = request.form['category']
        description = request.form['description']
        db = get_db()
        db.execute(
            'INSERT INTO complaints (user_id, category_id, description) VALUES (?, ?, ?)',
            (current_user.id, category, description)
        )
        db.commit()
        flash('Complaint submitted!')
        return redirect(url_for('track'))  # ✅ Always return a response

    # If GET (or any case that didn't hit POST)…
    categories = get_category_list()
    return render_template('submit.html', categories=categories)  # ✅ Also returns

def get_category_list():
    db = get_db()
    rows = db.execute('SELECT id, name FROM categories ORDER BY name').fetchall()
    # Return as list of tuples [(id, name), ...]
    return [(row['id'], row['name']) for row in rows]

@app.route('/track', methods=['GET', 'POST'])
def track():
    if request.method == 'POST':
        complaint_id = request.form.get('complaint_id')
        if complaint_id:
            complaint = get_complaint_details(complaint_id)
            if complaint:
                return render_template('track.html', complaint=complaint)
            else:
                flash('Complaint not found')
        else:
            flash('Please enter a complaint ID')
        return redirect(url_for('track'))

    return render_template('track.html')


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    db = get_db()
    complaints = db.execute(
        '''
        SELECT complaints.id, users.email, categories.name AS category,
               description, status, created_at, updated_at
        FROM complaints
        JOIN users ON complaints.user_id = users.id
        JOIN categories ON complaints.category_id = categories.id
        ORDER BY created_at DESC
        '''
    ).fetchall()

    # Handle status update form submit
    if request.method == 'POST':
        complaint_id = request.form.get('complaint_id')
        new_status = request.form.get('status')
        if complaint_id and new_status:
            db.execute(
                'UPDATE complaints SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                (new_status, complaint_id)
            )
            db.commit()
            flash('Status updated successfully')
        else:
            flash('Invalid update request')
        return redirect(url_for('admin'))  # ✅ Return a redirect after POST

    # Always return template when rendering page
    return render_template('admin.html', complaints=complaints)

if __name__ == '__main__':
    app.run(debug=True)
