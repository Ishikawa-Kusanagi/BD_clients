import psycopg2

def create_db(conn):
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                client_id SERIAL PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email VARCHAR(60),
                phones TEXT
            );
        """)
        conn.commit()
        print('База данных создана')

def add_client(conn, first_name, last_name, email, phones=None):
    with conn.cursor() as cursor:
        phones_str = ', '.join(phones) if phones else None
        cursor.execute("""
            INSERT INTO clients (first_name, last_name, email, phones) VALUES (%s, %s, %s, %s)
        """, (first_name, last_name, email, phones_str))
        conn.commit()
        print(f'Клиент добавлен, номер телефона: {phones_str if phones_str else None}')

def add_phone(conn, client_id, phone):
    with conn.cursor() as cursor:
        cursor.execute("""
            UPDATE clients
            SET phones = COALESCE(phones || ',', '') || %s
            WHERE client_id = %s
        """, (phone, client_id))
        conn.commit()
        print(f'Номер телефона {phone} добавлен для клиента с id {client_id}')

def change_client(conn, client_id, first_name=None, last_name=None, email=None, phones=None):
    try:
        with conn.cursor() as cursor:
            if first_name is not None:
                cursor.execute("UPDATE clients SET first_name = %s WHERE client_id = %s", (first_name, client_id))

            if last_name is not None:
                cursor.execute("UPDATE clients SET last_name = %s WHERE client_id = %s", (last_name, client_id))

            if email is not None:
                cursor.execute("UPDATE clients SET email = %s WHERE client_id = %s", (email, client_id))

            if phones is not None:
                phones_str = ', '.join(phones)
                cursor.execute("UPDATE clients SET phones = %s WHERE client_id = %s", (phones_str, client_id))

            conn.commit()
            print(f'Данные клиента с id {client_id} обновлены')

    except Exception as e:
        print(f'Произошла ошибка при изменении данных пользователя: {e}')

def delete_phone(conn, client_id, phone):
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT phones FROM clients WHERE client_id = %s", (client_id,))
            phones = cursor.fetchone()[0]
            if phones:
                phones_list = phones.split(', ')
                if phone in phones_list:
                    phones_list.remove(phone)
                    new_phones = ', '.join(phones_list) if phones_list else None
                    cursor.execute("UPDATE clients SET phones = %s WHERE client_id = %s", (new_phones, client_id))
                    conn.commit()
                    print(f'Номер телефона {phone} удален для клиента с id {client_id}')
                else:
                    print(f'Телефон {phone} не найден у клиента с id {client_id}')
            else:
                print(f'У клиента с id {client_id} нет телефонов')

    except Exception as e:
        print(f'Произошла ошибка при удалении телефона: {e}')

def delete_client(conn, client_id):
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM clients WHERE client_id = %s", (client_id,))
            conn.commit()
            print(f'Клиент с id {client_id} удален')

    except Exception as e:
        print(f'Произошла ошибка при удалении клиента: {e}')

def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    try:
        query = 'SELECT * FROM clients WHERE'
        conditions = []
        params = []
        if first_name:
            conditions.append("first_name = %s")
            params.append(first_name)
        if last_name:
            conditions.append("last_name = %s")
            params.append(last_name)
        if email:
            conditions.append("email = %s")
            params.append(email)
        if phone:
            conditions.append("phones LIKE %s")
            params.append(f'%{phone}%')
        if not conditions:
            return []
        query += " AND ".join(conditions)
        with conn.cursor() as cursor:
            cursor.execute(query, tuple(params))
            results = cursor.fetchall()
        return results
    except Exception as e:
        print(f'Ошибка: {e}')

with psycopg2.connect(database="clients_db", user="postgres", password="postgres") as conn:
    create_db(conn)
    add_client(conn, "Alex", "Balakin", "Balakin174@yandex.ru", ["9991299912"])
    add_phone(conn, 1, "0987654321")
    change_client(conn, 1, first_name="Serj", email="Serj@rambler.ru", phones=["112234152"])
    delete_phone(conn, 1, "0987654321")
    delete_client(conn, 1)
    clients = find_client(conn, first_name="Serj")
    print(clients)
