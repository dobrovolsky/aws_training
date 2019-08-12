import pg8000


class DBPostgres:
    def __init__(self, *args, **kwargs):
        self.conn = pg8000.connect(*args, **kwargs)
        self.apply_migrations()

    def apply_migrations(self):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS items_log (
                id serial PRIMARY KEY,
                created_at INTEGER,
                name VARCHAR(255),
                amount REAL,
                category VARCHAR(255)
            ); 
            """,
        )

    def save(self, prepared_data):
        cursor = self.conn.cursor()

        if prepared_data:
            cursor.executemany(
                "INSERT INTO items_log (created_at, name, amount, category) "
                "VALUES (%s, %s, %s, %s)", prepared_data)
            self.conn.commit()