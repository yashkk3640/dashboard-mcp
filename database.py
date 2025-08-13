from fastapi import APIRouter, HTTPException, Query
import re
from pydantic import BaseModel
import sqlite3
from typing import List
from contextlib import contextmanager

router = APIRouter()

# Create a single connection for the in-memory database
conn = sqlite3.connect(":memory:", check_same_thread=False)
conn.row_factory = sqlite3.Row

@contextmanager
def get_connection():
    try:
        yield conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Model for User data
class UserData(BaseModel):
    name: str
    email: str
    age: int

class TableInfo(BaseModel):
    name: str
    column: object

# Initialize database and create table
def init_db():
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            age INTEGER NOT NULL
        )
    """)
    conn.commit()

# Initialize the database when the module loads
init_db()

# Add some test data
try:
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
        ("Test User", "test@example.com", 25)
    )
    conn.commit()
except sqlite3.IntegrityError:
    pass  # Ignore if test data already exists

@router.get("/users", response_model=List[UserData])
async def get_users():
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, email, age FROM users")
            rows = cursor.fetchall()
            return [
                UserData(name=row['name'], email=row['email'], age=row['age'])
                for row in rows
            ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/users", response_model=UserData)
async def create_user(user: UserData):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
                (user.name, user.email, user.age)
            )
            conn.commit()
            return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}")
async def get_user(user_id: int):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name, email, age FROM users WHERE id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail="User not found")
            return UserData(name=row['name'], email=row['email'], age=row['age'])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/users/{user_id}")
async def delete_user(user_id: int):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "delete FROM users WHERE id = ?",
                (user_id,)
            )
            conn.commit()
            return "User Deleted"
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Create table as per user request in the database
@router.post("/create-table")
async def create_table(tableInfo:TableInfo):
    cursor = conn.cursor()
    print(tableInfo.name)
    # list_of_col = list(tableInfo.column.keys())
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {tableInfo.name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            {",\n".join(f"{key} {value} NOT NULL" for key, value in tableInfo.column.items())}
        )
    """)
    conn.commit()
    return "Table Create successfully"

# Add some test data
try:
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
        ("Test User", "test@example.com", 25)
    )
    conn.commit()
except sqlite3.IntegrityError:
    pass  # Ignore if test data already exists

@router.get("/get_data/{table_name}", response_model=List[object])
async def get_users(table_name:str):
    print(table_name)
    try:
        with get_connection() as conn:
            if not re.match(r'^[A-Z_]+$', table_name):
                raise ValueError("Invalid table name")
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add_data/{table_name}", response_model=object)
async def add_data_in_table(table_name: str, data: object ):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            col_names = []
            col_values= []

            for key,value in data.items():
                col_names.append(key)
                col_values.append(value)

            cursor.execute(
                "INSERT INTO ? (?) VALUES (?)",
                (table_name, ",".join(col_names), ",".join(col_values))
            )
            conn.commit()
            return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# @router.get("/users/{user_id}")
# async def get_user(user_id: int):
#     try:
#         with get_connection() as conn:
#             cursor = conn.cursor()
#             cursor.execute(
#                 "SELECT name, email, age FROM users WHERE id = ?",
#                 (user_id,)
#             )
#             row = cursor.fetchone()
#             if row is None:
#                 raise HTTPException(status_code=404, detail="User not found")
#             return UserData(name=row['name'], email=row['email'], age=row['age'])
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete_data/{table_name}/{id}")
async def delete_user9(table_name: str, id: int):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            if not re.match(r'^[A-Z_]+$', table_name):
                raise ValueError("Invalid table name")
            cursor.execute(
                f"delete FROM {table_name} WHERE id = ?",
                (id,)
            )
            conn.commit()
            return "User Deleted"
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
