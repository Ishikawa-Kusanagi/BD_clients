import psycopg2

def create_db(conn):
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                client_id SERIAL PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email VARCHAR(60)
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS phones (
                phone_id SERIAL PRIMARY KEY,
                client_id INTEGER NOT NULL REFERENCES clients(client_id) ON DELETE CASCADE,
                phone TEXT NOT NULL
            );
        """)
        conn.commit()
        print('База данных создана')

def add_client(conn, first_name, last_name, email, phones=None):
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO clients (first_name, last_name, email) VALUES (%s, %s, %s) RETURNING client_id
        """, (first_name, last_name, email))
        client_id = cursor.fetchone()[0]
        if phones:
            for phone in phones:
                cursor.execute("""
                    INSERT INTO phones (client_id, phone) VALUES (%s, %s)
                """, (client_id, phone))
        conn.commit()
        print(f'Клиент добавлен, ID: {client_id}')

def add_phone(conn, client_id, phone):
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO phones (client_id, phone) VALUES (%s, %s)
        """, (client_id, phone))
        conn.commit()
        print(f'Номер телефона {phone} добавлен для клиента с ID {client_id}')

def change_client(conn, client_id, first_name=None, last_name=None, email=None, phones=None):
    with conn.cursor() as cursor:
        if first_name is not None:
            cursor.execute("UPDATE clients SET first_name = %s WHERE client_id = %s", (first_name, client_id))
        if last_name is not None:
            cursor.execute("UPDATE clients SET last_name = %s WHERE client_id = %s", (last_name, client_id))
        if email is not None:
            cursor.execute("UPDATE clients SET email = %s WHERE client_id = %s", (email, client_id))
        if phones is not None:
            cursor.execute("DELETE FROM phones WHERE client_id = %s", (client_id,))
            for phone in phones:
                cursor.execute("INSERT INTO phones (client_id, phone) VALUES (%s, %s)", (client_id, phone))
        conn.commit()
        print(f'Данные клиента с ID {client_id} обновлены')

def delete_phone(conn, client_id, phone):
    with conn.cursor() as cursor:
        cursor.execute("""
            DELETE FROM phones WHERE client_id = %s AND phone = %s
        """, (client_id, phone))
        conn.commit()
        print(f'Номер телефона {phone} удален для клиента с ID {client_id}')

def delete_client(conn, client_id):
    with conn.cursor() as cursor:
        cursor.execute("""
            DELETE FROM clients WHERE client_id = %s
        """, (client_id,))
        conn.commit()
        print(f'Клиент с ID {client_id} удален')

def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    query = 'SELECT c.client_id, c.first_name, c.last_name, c.email, p.phone FROM clients c LEFT JOIN phones p ON c.client_id = p.client_id WHERE'
    conditions = []
    params = []
    if first_name:
        conditions.append("c.first_name = %s")
        params.append(first_name)
    if last_name:
        conditions.append("c.last_name = %s")
        params.append(last_name)
    if email:
        conditions.append("c.email = %s")
        params.append(email)
    if phone:
        conditions.append("p.phone = %s")
        params.append(phone)
    if not conditions:
        return []
    query += " AND ".join(conditions)
    with conn.cursor() as cursor:
        cursor.execute(query, tuple(params))
        results = cursor.fetchall()
    return results

if __name__ == "__main__":
    with psycopg2.connect(database="clients_db", user="postgres", password="postgres") as conn:
        create_db(conn)
        add_client(conn, "Alex", "Balakin", "Balakin174@yandex.ru", ["9991299912"])
        add_phone(conn, 1, "0987654321")
        change_client(conn, 1, first_name="Serj", email="Serj@rambler.ru", phones=["112234152"])
        delete_phone(conn, 1, "0987654321")
        delete_client(conn, 1)
        clients = find_client(conn, first_name="Serj")
        print(clients)
