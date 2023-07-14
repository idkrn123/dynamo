import os
import sqlite3

def test_add_balance():
    # Connect to your database
    conn = sqlite3.connect('/tmp/test.db')

    # Create a cursor object
    cur = conn.cursor()

    # Execute the SQL query
    cur.execute("UPDATE user SET balance = balance + 5")

    # Commit the changes
    conn.commit()

    # Close the cursor and connection
    cur.close()
    conn.close()