import sqlite3

# Replace 'your_database_file.db' with the path to your SQLite database file.
db_file = 'db.sqlite3'

# Connect to the SQLite database
conn = sqlite3.connect(db_file)

# Create a cursor
cursor = conn.cursor()

# Use the cursor to execute a query that retrieves the table schema
cursor.execute(f"SELECT * FROM django_migrations")

# Fetch all the columns (fields) in the table
migrations = cursor.fetchall()

# Extract the column names from the result

# Close the cursor and the database connection
cursor.close()
conn.close()

# Print the column names
for column_name in migrations:
    print(column_name)