import mysql.connector
import uuid

def open_connection():
# Connect to MySQL
    try:
        connection = mysql.connector.connect(
            host="localhost",     # Change to your MySQL server host
            user="root",          # Your MySQL username
            password="root@123",  # Your MySQL password
            database="ai_agent"   # Optional: Specify a database
        )
        
        if connection.is_connected():
            # print("[DEBUG] Connected to MySQL successfully!")

            # Execute a test query
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            db_name = cursor.fetchone()
            # print("[DEBUG] Connected to database:", db_name)

    except mysql.connector.Error as err:
        print("Error:", err)
        return None
    
    return connection

def close_connection(connection):
    if 'connection' in locals() and connection.is_connected():
        cursor = connection.cursor()
        cursor.close()
        connection.close()
        # print("[DEBUG] MySQL connection closed.")


shared_connection = open_connection()

def add_new_todo(todo, connection = shared_connection):
    if connection.is_connected() == False:
        connection = open_connection()

    sql = "INSERT INTO Todo (id, task) VALUES (%s, %s);"
    val = (uuid.uuid4(), todo)

    cursor = connection.cursor()
    cursor.execute(sql, (str(uuid.uuid4()), todo))
    connection.commit()
    # print("[DEBUG] New todo added:", todo)

def get_all_todos(connection = shared_connection):
    # if connection.is_connected() == False:
    #     connection = open_connection()

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Todo;")
    todos = cursor.fetchall()
    todos = [{"id": todo[0], "task": todo[1]} for todo in todos]
    return todos

def get_todo(task, connection = shared_connection):
    if connection.is_connected() == False:
        connection = open_connection()

    cursor = connection.cursor()
    query = "SELECT * FROM Todo WHERE task LIKE %s;"
    cursor.execute(query, ("%"+task+"%",))
    todo = cursor.fetchall()
    todo = [{"id": todo[0], "task": todo[1]} for todo in todo]
    return todo

def update_todo(todo, connection = shared_connection):
    if connection.is_connected() == False:
        connection = open_connection()

    cursor = connection.cursor()
    cursor.execute(f"UPDATE Todo SET task = {todo['task']} WHERE id = {todo['id']};")
    connection.commit()
    # print("[DEBUG] Todo updated:", todo)

def delete_todo(task, connection = shared_connection):
    if connection.is_connected() == False:
        connection = open_connection()

    try:
        todo = get_todo(task, connection)[0]
        todo = {"id": todo["id"], "task": todo["task"]}
        result = delete_todo_id(todo["id"], connection)
        return {"task": task, "result": result}   
    except Exception as e:
        print(e)
        return {"exception": str(e), "result": False}

def delete_todo_id(id, connection = shared_connection):  
    if connection.is_connected() == False:
        connection = open_connection()
        
    cursor = connection.cursor()
    query = "DELETE FROM Todo WHERE id = %s;"
    cursor.execute(query, (id,))
    connection.commit()
    # print("[DEBUG] Todo deleted:", id)
    return True