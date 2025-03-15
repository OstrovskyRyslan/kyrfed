import pyodbc

class DatabaseManager:
    """Класс для работы с базой данных."""

    def __init__(self):
        try:
            self.conn = pyodbc.connect(
                'DRIVER={ODBC Driver 17 for SQL Server};'
                'SERVER=DESKTOP-QQAOEK4;'
                'DATABASE=EventNotifierApp;'
                'Trusted_Connection=yes;'
                'Encrypt=yes;'
                'TrustServerCertificate=yes;'
            )
            self.cursor = self.conn.cursor()
            self.create_tables()
        except pyodbc.Error as e:
            raise Exception(f"Ошибка подключения к базе данных: {str(e)}")

    def create_tables(self):
        """Создание таблиц, если они не существуют."""
        queries = [
            '''IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' AND xtype='U')
               CREATE TABLE users (
                   id INT IDENTITY(1,1) PRIMARY KEY,
                   name NVARCHAR(100),
                   email NVARCHAR(100),
                   phone NVARCHAR(20),
                   contact_method NVARCHAR(20)
               )''',
            '''IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='messages' AND xtype='U')
               CREATE TABLE messages (
                   id INT IDENTITY(1,1) PRIMARY KEY,
                   user_id INT,
                   message NVARCHAR(1000),
                   FOREIGN KEY (user_id) REFERENCES users(id)
               )''',
            '''IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='events' AND xtype='U')
               CREATE TABLE events (
                   id INT IDENTITY(1,1) PRIMARY KEY,
                   user_id INT,
                   event_date DATETIME,
                   event_description NVARCHAR(1000),
                   FOREIGN KEY (user_id) REFERENCES users(id)
               )'''
        ]
        for query in queries:
            self.cursor.execute(query)
        self.conn.commit()

    def execute_query(self, query, params=(), fetch=False):
        """Выполнить SQL-запрос."""
        with self.conn.cursor() as cursor:
            cursor.execute(query, params)
            if fetch:
                return cursor.fetchall()
            self.conn.commit()
