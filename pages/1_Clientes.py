import streamlit as st
import db
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import inject_css, ensure_auth, sidebar_nav, inject_session_persistence


def main():
	st.set_page_config(
		page_title="Clientes | Encomendas de Bolos", 
		page_icon="👥", 
		layout="wide",
		menu_items={
			'Get Help': None,
			'Report a bug': None,
			'About': None
		}
	)
	inject_css()
	inject_session_persistence()
	ensure_auth()
	a = st.session_state.auth

	st.markdown("## 👥 Gerenciar Clientes")

	with st.expander("Adicionar cliente", expanded=True):
		with st.form("add_client_form"):
			name = st.text_input("Nome do cliente")
			phone = st.text_input("Telefone")
			notes = st.text_area("Observações")
			sub = st.form_submit_button("Salvar")
			if sub:
				if not name.strip():
					st.error("Nome é obrigatório.")
				else:
					db.create_client(a["user_id"], name.strip(), phone.strip() if phone else None, notes.strip() if notes else None)
					st.success("Cliente cadastrado!")
					st.rerun()

	st.markdown("---")

	clients = db.list_clients(a["user_id"]) or []
	if not clients:
		st.info("Nenhum cliente cadastrado.")
		return

	for c in clients:
		with st.expander(f"👤 {c['name']}"):
			col1, col2 = st.columns([0.5, 0.5])
			with col1:
				st.markdown("**Telefone**")
				st.write(c["phone"] or "-")
			with col2:
				st.markdown("**Observações**")
				st.write(c["notes"] or "-")

			st.markdown("---")
			st.markdown("**Encomendas deste cliente**")
			orders = db.list_orders_by_client(a["user_id"], c["id"]) or []
			if not orders:
				st.caption("Sem encomendas.")
			else:
				for o in orders:
					cols = st.columns([0.25, 0.25, 0.2, 0.15, 0.15])
					with cols[0]:
						st.write(f"Sabor: {o['flavor']}")
					with cols[1]:
						st.caption(f"Tamanho: {o['size'] or '-'}")
					with cols[2]:
						st.caption(f"Entrega: {o['due_date']}")
					with cols[3]:
						st.caption(f"Preço: R$ {o['price'] if o['price'] is not None else '-'}")
					with cols[4]:
						st.caption(f"Status: {o['status']}")

			st.markdown("---")
			
			# Botões de ação
			col_btn1, col_btn2 = st.columns([0.5, 0.5])
			with col_btn1:
				if st.button("✏️ Atualizar dados", key=f"edit_{c['id']}"):
					st.session_state[f"editing_client_{c['id']}"] = True
					st.rerun()
			
			with col_btn2:
				if st.button("🗑️ Remover cliente", key=f"del_{c['id']}"):
					db.delete_client(a["user_id"], c["id"])
					st.success("Cliente removido.")
					st.rerun()
			
			# Formulário de edição
			if st.session_state.get(f"editing_client_{c['id']}", False):
				st.markdown("### Editar Cliente")
				with st.form(f"edit_client_form_{c['id']}"):
					new_name = st.text_input("Nome do cliente", value=c["name"], key=f"edit_name_{c['id']}")
					new_phone = st.text_input("Telefone", value=c["phone"] or "", key=f"edit_phone_{c['id']}")
					new_notes = st.text_area("Observações", value=c["notes"] or "", key=f"edit_notes_{c['id']}")
					
					col_save, col_cancel = st.columns([0.5, 0.5])
					with col_save:
						if st.form_submit_button("💾 Salvar alterações"):
							if new_name.strip():
								db.update_client(a["user_id"], c["id"], new_name.strip(), new_phone.strip() if new_phone else None, new_notes.strip() if new_notes else None)
								st.success("Cliente atualizado!")
								st.session_state[f"editing_client_{c['id']}"] = False
								st.rerun()
							else:
								st.error("Nome é obrigatório.")
					
					with col_cancel:
						if st.form_submit_button("❌ Cancelar"):
							st.session_state[f"editing_client_{c['id']}"] = False
							st.rerun()


if __name__ == "__main__":
	main()
