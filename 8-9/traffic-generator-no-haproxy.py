import psycopg2
import time
import random
from datetime import datetime

DB_NODES = [
    {"host": "localhost", "port": 5433, "user": "postgres", "password": "postgres", "dbname": "postgres"},
    {"host": "localhost", "port": 5434, "user": "postgres", "password": "postgres", "dbname": "postgres"}, 
    {"host": "localhost", "port": 5435, "user": "postgres", "password": "postgres", "dbname": "postgres"}
]

EVENT_TYPES = ['login', 'logout', 'click', 'purchase', 'view_page', 'error']

def find_leader():
    """Находит лидера в кластере Patroni"""
    for node in DB_NODES:
        try:
            print(f"Проверяем ноду {node['host']}:{node['port']}...")
            conn = psycopg2.connect(**node)
            cur = conn.cursor()
            
            cur.execute("SELECT pg_is_in_recovery(), inet_server_addr(), inet_server_port()")
            is_replica, host, port = cur.fetchone()
            
            if not is_replica:
                print(f"Найден ЛИДЕР: {host}:{port}")
                cur.close()
                return conn
            else:
                print(f"Нода {host}:{port} - реплика (read-only)")
                cur.close()
                conn.close()
                
        except psycopg2.OperationalError as e:
            print(f"Нода {node['host']}:{node['port']} недоступна: {e}")
        except Exception as e:
            print(f"Ошибка при проверке {node['host']}:{node['port']}: {e}")
    
    return None

def get_random_owner(conn):
    """Получает случайного овнера из справочника"""
    try:
        cur = conn.cursor()
        cur.execute("SELECT owner_name FROM owners ORDER BY RANDOM() LIMIT 1;")
        result = cur.fetchone()
        cur.close()
        return result[0] if result else "Unknown"
    except Exception as e:
        print(f"Ошибка при получении owner: {e}")
        return "Unknown"

def get_current_node_info(conn):
    """Получает информацию о текущей ноде"""
    try:
        cur = conn.cursor()
        cur.execute("SELECT pg_is_in_recovery(), inet_server_addr(), inet_server_port()")
        is_replica, host, port = cur.fetchone()
        cur.close()
        return is_replica, host, port
    except:
        return None, "unknown", "unknown"

def main():
    print("Starting Direct Patroni Connection Demo")
    print("=" * 50)
    
    conn = None
    tick = 0

    while True:
        try:
            current_time = datetime.now().strftime('%H:%M:%S')
            
            # Если соединения нет или оно разорвано - ищем лидера
            if conn is None or conn.closed:
                print(f"\n[{current_time}] Поиск лидера в кластере...")
                conn = find_leader()
                
                if conn is None:
                    print("Лидер не найден! Повторная попытка через 5 секунд...")
                    time.sleep(5)
                    continue
                
                # Показываем информацию о подключенной ноде
                is_replica, host, port = get_current_node_info(conn)
                node_type = "РЕПЛИКА" if is_replica else "ЛИДЕР"
                print(f"Подключено к {node_type}: {host}:{port}")

            # Получаем случайного owner
            owner = get_random_owner(conn)
            event = random.choice(EVENT_TYPES)
            
            # Пытаемся выполнить запрос
            cur = conn.cursor()
            
            # ВСТАВКА данных
            insert_query = "INSERT INTO events (event_name, owner_name) VALUES (%s, %s) RETURNING id"
            cur.execute(insert_query, (event, owner))
            new_id = cur.fetchone()[0]
            conn.commit()
            
            # Показываем детали операции
            is_replica, host, port = get_current_node_info(conn)
            node_type = "REPLICA" if is_replica else "LEADER"
            
            print(f"[{current_time}] INSERT #{new_id} on {node_type} {host}:{port} - {event} by {owner}")

            # ЧТЕНИЕ каждые 3 секунды
            if tick % 3 == 0:
                cur.execute("SELECT id, event_name, owner_name FROM events ORDER BY id DESC LIMIT 3")
                rows = cur.fetchall()
                print(f"Последние 3 записи: {[r[0] for r in rows]}")
            
            cur.close()
            tick += 1
            time.sleep(2)

        except psycopg2.OperationalError as e:
            print(f"\n[{current_time}] Ошибка подключения: {e}")
            print("   Вероятно, лидер изменился. Переподключаемся...")
            if conn and not conn.closed:
                try:
                    conn.close()
                except:
                    pass
            conn = None
            time.sleep(3)
            
        except psycopg2.InterfaceError as e:
            print(f"\n[{current_time}] Разрыв соединения: {e}")
            conn = None
            time.sleep(3)
            
        except Exception as e:
            print(f"\n[{current_time}] Неожиданная ошибка: {e}")
            conn = None
            time.sleep(3)

if __name__ == "__main__":
    main()