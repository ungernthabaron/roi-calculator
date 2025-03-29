import sqlite3
import hashlib
from datetime import datetime
import json

def init_db():
    conn = sqlite3.connect('impact_calculator.db')
    c = conn.cursor()
    
    # Create users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  role TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Create projects table
    c.execute('''CREATE TABLE IF NOT EXISTS projects
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  description TEXT,
                  project_type TEXT NOT NULL,
                  status TEXT DEFAULT 'submitted',
                  customer_id INTEGER,
                  pm_estimate REAL,
                  it_director_estimate REAL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (customer_id) REFERENCES users (id))''')
    
    # Create project inputs table
    c.execute('''CREATE TABLE IF NOT EXISTS project_inputs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  project_id INTEGER,
                  input_type TEXT NOT NULL,
                  value REAL NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (project_id) REFERENCES projects (id))''')
    
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password, role):
    conn = sqlite3.connect('impact_calculator.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                 (username, hash_password(password), role))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(username, password):
    conn = sqlite3.connect('impact_calculator.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?',
             (username, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return user

def create_project(title, description, project_type, customer_id):
    conn = sqlite3.connect('impact_calculator.db')
    c = conn.cursor()
    try:
        c.execute('''INSERT INTO projects (title, description, project_type, customer_id)
                     VALUES (?, ?, ?, ?)''', (title, description, project_type, customer_id))
        project_id = c.lastrowid
        conn.commit()
        print(f"Project created successfully with ID: {project_id}")
        return project_id
    except Exception as e:
        print(f"Error creating project: {e}")
        return None
    finally:
        conn.close()

def get_user_projects(user_id):
    conn = sqlite3.connect('impact_calculator.db')
    c = conn.cursor()
    c.execute('SELECT * FROM projects WHERE customer_id = ?', (user_id,))
    projects = c.fetchall()
    conn.close()
    return projects

def get_all_projects():
    conn = sqlite3.connect('impact_calculator.db')
    c = conn.cursor()
    try:
        print("\n=== Database Status ===")
        
        # Проверим все проекты без JOIN
        print("\n=== Projects without JOIN ===")
        c.execute('SELECT * FROM projects')
        raw_projects = c.fetchall()
        print(f"Total projects: {len(raw_projects)}")
        for p in raw_projects:
            print(f"Project ID: {p[0]}, Title: {p[1]}, Status: {p[4]}")
        
        # Проверим пользователей
        print("\n=== Users ===")
        c.execute('SELECT * FROM users')
        users = c.fetchall()
        print(f"Total users: {len(users)}")
        for u in users:
            print(f"User ID: {u[0]}, Username: {u[1]}, Role: {u[3]}")
        
        # Получаем проекты с JOIN
        print("\n=== Projects with JOIN ===")
        c.execute('''SELECT p.*, u.username as customer_name 
                     FROM projects p 
                     LEFT JOIN users u ON p.customer_id = u.id''')
        projects = c.fetchall()
        print(f"Retrieved {len(projects)} projects with JOIN")
        
        for project in projects:
            print(f"\nProject details:")
            print(f"ID: {project[0]}")
            print(f"Title: {project[1]}")
            print(f"Status: {project[4]}")
            print(f"Customer ID: {project[5]}")
            print(f"Customer Name: {project[9]}")
            
        return projects
    except Exception as e:
        print(f"Error getting projects: {e}")
        return []
    finally:
        conn.close()

def update_project_status(project_id, status, estimate=None):
    conn = sqlite3.connect('impact_calculator.db')
    c = conn.cursor()
    try:
        print(f"\n=== Updating project {project_id} status to {status} ===")
        
        # Проверим текущий статус проекта
        c.execute('SELECT status FROM projects WHERE id = ?', (project_id,))
        current_status = c.fetchone()
        print(f"Current project status: {current_status[0] if current_status else 'Not found'}")
        
        if estimate is not None:
            c.execute('UPDATE projects SET status = ?, pm_estimate = ? WHERE id = ?', (status, estimate, project_id))
            print(f"Updated project {project_id} with status {status} and estimate {estimate}")
        else:
            c.execute('UPDATE projects SET status = ? WHERE id = ?', (status, project_id))
            print(f"Updated project {project_id} with status {status}")
        
        # Проверим новый статус
        c.execute('SELECT status FROM projects WHERE id = ?', (project_id,))
        new_status = c.fetchone()
        print(f"New project status: {new_status[0] if new_status else 'Not found'}")
        
        conn.commit()
    except Exception as e:
        print(f"Error updating project status: {e}")
    finally:
        conn.close()

def save_project_inputs(project_id, inputs):
    """Save project inputs to the database"""
    try:
        # First, delete existing inputs for this project
        conn = sqlite3.connect('impact_calculator.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM project_inputs WHERE project_id = ?", (project_id,))
        
        # Insert new inputs
        for input_type, value in inputs.items():
            # Convert dictionary to JSON string if value is a dictionary
            if isinstance(value, dict):
                value = json.dumps(value)
            # Convert list to JSON string if value is a list
            elif isinstance(value, list):
                value = json.dumps(value)
            
            cursor.execute("""
                INSERT INTO project_inputs (project_id, input_type, value)
                VALUES (?, ?, ?)
            """, (project_id, input_type, value))
        
        conn.commit()
        print(f"Successfully saved inputs for project {project_id}")
        
    except Exception as e:
        print(f"Error saving project inputs: {str(e)}")
        conn.rollback()
        raise

def get_project_inputs(project_id):
    """Get all inputs for a specific project"""
    try:
        conn = sqlite3.connect('impact_calculator.db')
        cursor = conn.cursor()
        
        print(f"\n=== Getting inputs for project {project_id} ===")
        
        # Get all inputs for the project
        cursor.execute("""
            SELECT input_type, value
            FROM project_inputs
            WHERE project_id = ?
        """, (project_id,))
        
        inputs = {}
        for input_type, value in cursor.fetchall():
            try:
                # Try to parse JSON if the value looks like a JSON string
                if isinstance(value, str) and (value.startswith('{') or value.startswith('[')):
                    value = json.loads(value)
                # Convert numeric strings to float
                elif isinstance(value, str) and value.replace('.', '').isdigit():
                    value = float(value)
                inputs[input_type] = value
            except json.JSONDecodeError:
                # If not JSON, keep the original value
                inputs[input_type] = value
        
        print(f"Final input dictionary: {inputs}")
        return inputs
        
    except Exception as e:
        print(f"Error getting project inputs: {str(e)}")
        return {}
    finally:
        if conn:
            conn.close()

def check_database():
    conn = sqlite3.connect('impact_calculator.db')
    c = conn.cursor()
    try:
        print("\n=== Database Content Check ===")
        
        # Check users table
        print("\nUsers table:")
        c.execute('SELECT * FROM users')
        users = c.fetchall()
        for user in users:
            print(f"ID: {user[0]}, Username: {user[1]}, Role: {user[3]}")
        
        # Check projects table
        print("\nProjects table:")
        c.execute('SELECT * FROM projects')
        projects = c.fetchall()
        for project in projects:
            print(f"ID: {project[0]}, Title: {project[1]}, Customer ID: {project[5]}, Status: {project[4]}")
        
        # Check project inputs table
        print("\nProject inputs table:")
        c.execute('SELECT * FROM project_inputs')
        inputs = c.fetchall()
        for input in inputs:
            print(f"ID: {input[0]}, Project ID: {input[1]}, Type: {input[2]}, Value: {input[3]}")
            
    except Exception as e:
        print(f"Error checking database: {e}")
    finally:
        conn.close()

def get_projects_by_status(status):
    conn = sqlite3.connect('impact_calculator.db')
    c = conn.cursor()
    try:
        print(f"\n=== Getting projects with status: {status} ===")
        
        # Сначала проверим все проекты
        c.execute('SELECT * FROM projects')
        all_projects = c.fetchall()
        print(f"Total projects in database: {len(all_projects)}")
        for p in all_projects:
            print(f"Project ID: {p[0]}, Title: {p[1]}, Status: {p[4]}")
        
        # Теперь получим проекты с нужным статусом
        c.execute('''SELECT p.*, u.username as customer_name 
                     FROM projects p 
                     LEFT JOIN users u ON p.customer_id = u.id
                     WHERE p.status = ?''', (status,))
        projects = c.fetchall()
        print(f"Found {len(projects)} projects with status {status}")
        
        for project in projects:
            print(f"\nProject details:")
            print(f"ID: {project[0]}")
            print(f"Title: {project[1]}")
            print(f"Status: {project[4]}")
            print(f"Customer ID: {project[5]}")
            print(f"Customer Name: {project[9]}")
            
        return projects
    except Exception as e:
        print(f"Error getting projects by status: {e}")
        return []
    finally:
        conn.close()

def get_project(project_id):
    """Get a specific project by ID"""
    conn = sqlite3.connect('impact_calculator.db')
    c = conn.cursor()
    try:
        c.execute('''
            SELECT p.*, u.username as customer_name
            FROM projects p
            LEFT JOIN users u ON p.customer_id = u.id
            WHERE p.id = ?
        ''', (project_id,))
        project = c.fetchone()
        return project
    except Exception as e:
        print(f"Error getting project: {e}")
        return None
    finally:
        conn.close() 