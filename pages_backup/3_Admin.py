import streamlit as st
import db
from auth import hash_password
from utils import inject_css, ensure_superuser, sidebar_nav


def main():
	st.set_page_config(
		page_title="Admin | Encomendas de Bolos", 
		page_icon="⚙️", 
		layout="wide",
		menu_items={
			'Get Help': None,
			'Report a bug': None,
			'About': None
		}
	)
	inject_css()
	ensure_superuser()
	sidebar_nav()

	st.markdown("## Administração")

	# Alterar senha do próprio superuser
	with st.expander("Alterar minha senha", expanded=True):
		with st.form("change_pw"):
			new_pw = st.text_input("Nova senha", type="password")
			confirm_pw = st.text_input("Confirmar senha", type="password")
			sub = st.form_submit_button("Atualizar")
			if sub:
				if not new_pw or len(new_pw) < 6:
					st.error("Use ao menos 6 caracteres.")
				elif new_pw != confirm_pw:
					st.error("Senhas não conferem.")
				else:
					db.update_user_password(st.session_state.auth["user_id"], hash_password(new_pw))
					st.success("Senha atualizada!")

	st.markdown("---")

	# Gerenciar docerias (usuários)
	st.markdown("### Usuários (Docerias)")
	with st.form("add_user"):
		username = st.text_input("Usuário")
		bakery = st.text_input("Nome da doceria")
		email = st.text_input("Email")
		password = st.text_input("Senha", type="password")
		is_super = st.checkbox("Superusuário?", value=False)
		sub = st.form_submit_button("Criar usuário")
		if sub:
			if not username or not password:
				st.error("Usuário e senha são obrigatórios.")
			else:
				try:
					db.create_user(username, hash_password(password), bakery or None, email or None, is_super)
					st.success("Usuário criado!")
				except Exception as e:
					st.error(f"Erro ao criar usuário: {e}")

	users = db.list_users()
	for u in users:
		cols = st.columns([0.25, 0.25, 0.25, 0.25])
		with cols[0]:
			st.write(f"{u['username']}")
		with cols[1]:
			st.caption(u["bakery_name"] or "-")
		with cols[2]:
			st.caption("Superusuário" if u["is_superuser"] else "Usuário")
		with cols[3]:
			st.caption(u["email"] or "-")


if __name__ == "__main__":
	main()
