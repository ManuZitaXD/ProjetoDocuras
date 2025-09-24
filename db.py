import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Optional, Dict
from datetime import datetime
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# String de conexão do NeonDB
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://neondb_owner:npg_xSteZyJ1oE9A@ep-broad-bush-ad7mo2ty-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
)


def get_connection() -> psycopg2.extensions.connection:
	conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
	return conn


def init_db() -> None:
	conn = get_connection()
	cur = conn.cursor()

	# Users (docerias e superusuários)
	cur.execute(
		"""
		CREATE TABLE IF NOT EXISTS users (
			id SERIAL PRIMARY KEY,
			username VARCHAR(255) UNIQUE NOT NULL,
			password_hash TEXT NOT NULL,
			bakery_name VARCHAR(255),
			email VARCHAR(255),
			is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
			created_at TIMESTAMP NOT NULL
		)
		"""
	)

	# Clients por usuário/doceria
	cur.execute(
		"""
		CREATE TABLE IF NOT EXISTS clients (
			id SERIAL PRIMARY KEY,
			user_id INTEGER NOT NULL,
			name VARCHAR(255) NOT NULL,
			phone VARCHAR(50),
			notes TEXT,
			created_at TIMESTAMP NOT NULL,
			FOREIGN KEY (user_id) REFERENCES users (id)
		)
		"""
	)

	# Orders (encomendas)
	cur.execute(
		"""
		CREATE TABLE IF NOT EXISTS orders (
			id SERIAL PRIMARY KEY,
			user_id INTEGER NOT NULL,
			client_id INTEGER NOT NULL,
			flavor VARCHAR(255) NOT NULL,
			size VARCHAR(100),
			price DECIMAL(10,2),
			due_date DATE NOT NULL,
			status VARCHAR(100) NOT NULL,
			notes TEXT,
			created_at TIMESTAMP NOT NULL,
			paid_at TIMESTAMP,
			delivered_at TIMESTAMP,
			FOREIGN KEY (user_id) REFERENCES users (id),
			FOREIGN KEY (client_id) REFERENCES clients (id)
		)
		"""
	)

	conn.commit()

	# Seed de superusuário padrão se nenhum usuário existir
	cur.execute("SELECT COUNT(*) AS c FROM users")
	count = cur.fetchone()["c"]
	if count == 0:
		from auth import hash_password  # lazy import para evitar ciclo
		cur.execute(
			"""
			INSERT INTO users (username, password_hash, bakery_name, email, is_superuser, created_at)
			VALUES (%s, %s, %s, %s, %s, %s)
			""",
			(
				"admin",
				hash_password("admin123"),
				"Admin",
				"admin@example.com",
				True,
				datetime.utcnow(),
			),
		)
		conn.commit()

	cur.close()
	conn.close()


# USERS

def create_user(username: str, password_hash: str, bakery_name: Optional[str], email: Optional[str], is_superuser: bool) -> int:
	conn = get_connection()
	cur = conn.cursor()
	cur.execute(
		"""
		INSERT INTO users (username, password_hash, bakery_name, email, is_superuser, created_at)
		VALUES (%s, %s, %s, %s, %s, %s)
		RETURNING id
		""",
		(username, password_hash, bakery_name, email, is_superuser, datetime.utcnow()),
	)
	user_id = cur.fetchone()["id"]
	conn.commit()
	cur.close()
	conn.close()
	return user_id


def get_user_by_username(username: str) -> Optional[Dict]:
	conn = get_connection()
	cur = conn.cursor()
	cur.execute("SELECT * FROM users WHERE username = %s", (username,))
	row = cur.fetchone()
	cur.close()
	conn.close()
	return dict(row) if row else None


def get_user_by_id(user_id: int) -> Optional[Dict]:
	conn = get_connection()
	cur = conn.cursor()
	cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
	row = cur.fetchone()
	cur.close()
	conn.close()
	return dict(row) if row else None


def list_users() -> List[Dict]:
	conn = get_connection()
	cur = conn.cursor()
	cur.execute("SELECT * FROM users ORDER BY created_at DESC")
	rows = cur.fetchall()
	cur.close()
	conn.close()
	return [dict(row) for row in rows]


def update_user_password(user_id: int, new_password_hash: str) -> None:
	conn = get_connection()
	cur = conn.cursor()
	cur.execute("UPDATE users SET password_hash = %s WHERE id = %s", (new_password_hash, user_id))
	conn.commit()
	cur.close()
	conn.close()


def delete_user(user_id: int) -> None:
	conn = get_connection()
	cur = conn.cursor()
	# Primeiro deletar todas as encomendas do usuário
	cur.execute("DELETE FROM orders WHERE user_id = %s", (user_id,))
	# Depois deletar todos os clientes do usuário
	cur.execute("DELETE FROM clients WHERE user_id = %s", (user_id,))
	# Por último deletar o usuário
	cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
	conn.commit()
	cur.close()
	conn.close()


# CLIENTS

def create_client(user_id: int, name: str, phone: Optional[str], notes: Optional[str]) -> int:
	conn = get_connection()
	cur = conn.cursor()
	cur.execute(
		"""
		INSERT INTO clients (user_id, name, phone, notes, created_at)
		VALUES (%s, %s, %s, %s, %s)
		RETURNING id
		""",
		(user_id, name, phone, notes, datetime.utcnow()),
	)
	client_id = cur.fetchone()["id"]
	conn.commit()
	cur.close()
	conn.close()
	return client_id


def list_clients(user_id: int) -> List[Dict]:
	conn = get_connection()
	cur = conn.cursor()
	cur.execute("SELECT * FROM clients WHERE user_id = %s ORDER BY name", (user_id,))
	rows = cur.fetchall()
	cur.close()
	conn.close()
	return [dict(row) for row in rows]


def update_client(user_id: int, client_id: int, name: str, phone: Optional[str], notes: Optional[str]) -> None:
	conn = get_connection()
	cur = conn.cursor()
	cur.execute(
		"UPDATE clients SET name = %s, phone = %s, notes = %s WHERE user_id = %s AND id = %s",
		(name, phone, notes, user_id, client_id)
	)
	conn.commit()
	cur.close()
	conn.close()


def delete_client(user_id: int, client_id: int) -> None:
	conn = get_connection()
	cur = conn.cursor()
	# Também apagamos encomendas do cliente
	cur.execute("DELETE FROM orders WHERE user_id = %s AND client_id = %s", (user_id, client_id))
	cur.execute("DELETE FROM clients WHERE user_id = %s AND id = %s", (user_id, client_id))
	conn.commit()
	cur.close()
	conn.close()


# ORDERS

def create_order(
	user_id: int,
	client_id: int,
	flavor: str,
	size: Optional[str],
	price: Optional[float],
	due_date_iso: str,
	status: str,
	notes: Optional[str],
) -> int:
	conn = get_connection()
	cur = conn.cursor()
	cur.execute(
		"""
		INSERT INTO orders (user_id, client_id, flavor, size, price, due_date, status, notes, created_at)
		VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
		RETURNING id
		""",
		(
			user_id,
			client_id,
			flavor,
			size,
			price,
			due_date_iso,
			status,
			notes,
			datetime.utcnow(),
		),
	)
	order_id = cur.fetchone()["id"]
	conn.commit()
	cur.close()
	conn.close()
	return order_id


def list_orders(user_id: int) -> List[Dict]:
	conn = get_connection()
	cur = conn.cursor()
	cur.execute(
		"""
		SELECT o.*, c.name AS client_name
		FROM orders o
		JOIN clients c ON c.id = o.client_id
		WHERE o.user_id = %s
		ORDER BY o.due_date ASC, o.created_at DESC
		""",
		(user_id,),
	)
	rows = cur.fetchall()
	cur.close()
	conn.close()
	return [dict(row) for row in rows]


def list_orders_by_client(user_id: int, client_id: int) -> List[Dict]:
	conn = get_connection()
	cur = conn.cursor()
	cur.execute(
		"""
		SELECT o.*, c.name AS client_name
		FROM orders o
		JOIN clients c ON c.id = o.client_id
		WHERE o.user_id = %s AND o.client_id = %s
		ORDER BY o.due_date ASC, o.created_at DESC
		""",
		(user_id, client_id),
	)
	rows = cur.fetchall()
	cur.close()
	conn.close()
	return [dict(row) for row in rows]


def update_order_status(user_id: int, order_id: int, status: str) -> None:
	conn = get_connection()
	cur = conn.cursor()
	timestamp_field = None
	if status.startswith("Pago"):
		timestamp_field = "paid_at"
	elif status == "Entregue":
		timestamp_field = "delivered_at"

	if timestamp_field:
		cur.execute(
			f"UPDATE orders SET status = %s, {timestamp_field} = %s WHERE user_id = %s AND id = %s",
			(status, datetime.utcnow(), user_id, order_id),
		)
	else:
		cur.execute(
			"UPDATE orders SET status = %s WHERE user_id = %s AND id = %s",
			(status, user_id, order_id),
		)
	conn.commit()
	cur.close()
	conn.close()


def delete_order(user_id: int, order_id: int) -> None:
	conn = get_connection()
	cur = conn.cursor()
	cur.execute("DELETE FROM orders WHERE user_id = %s AND id = %s", (user_id, order_id))
	conn.commit()
	cur.close()
	conn.close()


def stats_counts(user_id: int) -> Dict[str, int]:
	conn = get_connection()
	cur = conn.cursor()
	statuses = ["Pendente", "Pago (Em preparação)", "Entregue"]
	result: Dict[str, int] = {s: 0 for s in statuses}
	for s in statuses:
		cur.execute("SELECT COUNT(*) AS c FROM orders WHERE user_id = %s AND status = %s", (user_id, s))
		result[s] = cur.fetchone()["c"]
	cur.close()
	conn.close()
	return result
