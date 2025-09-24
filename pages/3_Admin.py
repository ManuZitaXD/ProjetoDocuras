import streamlit as st
import db
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth import hash_password
from utils import inject_css, ensure_superuser, sidebar_nav, inject_session_persistence


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
	inject_session_persistence()
	ensure_superuser()

	st.markdown("## ⚙️ Administração")

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
	if not users:
		st.info("Nenhum usuário cadastrado.")
		return
	
	st.markdown("### Lista de Usuários")
	for u in users:
		with st.expander(f"👤 {u['username']} {'(Superusuário)' if u['is_superuser'] else ''}"):
			col1, col2 = st.columns([0.7, 0.3])
			with col1:
				st.markdown(f"**Nome da Doceria:** {u['bakery_name'] or '-'}")
				st.markdown(f"**Email:** {u['email'] or '-'}")
				st.markdown(f"**Tipo:** {'Superusuário' if u['is_superuser'] else 'Usuário'}")
				st.markdown(f"**Criado em:** {u['created_at'].strftime('%d/%m/%Y %H:%M') if u['created_at'] else '-'}")
			
			with col2:
				# Não permitir deletar o próprio usuário
				if u['id'] != st.session_state.auth["user_id"]:
					if st.button("🗑️ Remover Usuário", key=f"delete_user_{u['id']}", type="secondary"):
						# Confirmar antes de deletar
						if st.session_state.get(f"confirm_delete_{u['id']}", False):
							db.delete_user(u['id'])
							st.success(f"Usuário {u['username']} removido com sucesso!")
							st.session_state[f"confirm_delete_{u['id']}"] = False
							st.rerun()
						else:
							st.session_state[f"confirm_delete_{u['id']}"] = True
							st.warning("Clique novamente para confirmar a remoção")
							st.rerun()
					
					# Mostrar confirmação se necessário
					if st.session_state.get(f"confirm_delete_{u['id']}", False):
						st.error("⚠️ Clique novamente no botão para confirmar a remoção")
				else:
					st.info("Você não pode remover a si mesmo")


if __name__ == "__main__":
	main()
