import sqlite3

def init_db():
    conn = sqlite3.connect('complaints.db')  # creates the file
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print("Initialized database: complaints.db")

if __name__ == '__main__':
    init_db()
