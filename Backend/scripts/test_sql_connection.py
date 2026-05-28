from sqlalchemy import text

from app.db.session import engine


def main():
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT DB_NAME() AS database_name, SUSER_SNAME() AS login_name")
        ).mappings().first()

        print("Conexión exitosa a Azure SQL")
        print(f"Base de datos: {row['database_name']}")
        print(f"Login SQL: {row['login_name']}")

        tables = conn.execute(
            text("""
                SELECT TABLE_NAME
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
            """)
        ).fetchall()

        print("Tablas encontradas:")
        for table in tables:
            print(f" - {table[0]}")


if __name__ == "__main__":
    main()
