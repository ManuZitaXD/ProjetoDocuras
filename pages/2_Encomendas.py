import streamlit as st
from datetime import date
import db
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import inject_css, ensure_auth, sidebar_nav, inject_session_persistence, logout_button

STATUS_OPTIONS = ["Pendente", "Pago (Em preparação)", "Entregue"]


def main():
	st.set_page_config(
		page_title="Encomendas | Encomendas de Bolos", 
		page_icon="🧾", 
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

	# Botão de logout na sidebar
	logout_button()

	st.markdown("## 🧾 Encomendas")

	clients = db.list_clients(a["user_id"]) or []
	client_options = {c["name"]: c["id"] for c in clients}

	with st.expander("Adicionar encomenda", expanded=True):
		with st.form("add_order_form"):
			client_name = st.selectbox("Cliente", list(client_options.keys()) if client_options else ["Nenhum cliente"], disabled=not client_options)
			flavor = st.text_input("Sabor do bolo")
			size = st.text_input("Tamanho (ex: 1kg, 20cm)")
			price = st.number_input("Preço (R$)", min_value=0.0, step=0.5, format="%.2f")
			due = st.date_input("Data de entrega", value=date.today())
			status = st.selectbox("Status", STATUS_OPTIONS, index=0)
			notes = st.text_area("Observações")
			sub = st.form_submit_button("Salvar")
			if sub:
				if not client_options:
					st.error("Cadastre um cliente antes.")
				elif not flavor.strip():
					st.error("Sabor é obrigatório.")
				else:
					db.create_order(
						a["user_id"],
						client_options[client_name],
						flavor.strip(),
						size.strip() if size else None,
						float(price) if price else None,
						due.isoformat(),
						status,
						notes.strip() if notes else None,
					)
					st.success("Encomenda adicionada!")
					st.rerun()

	st.markdown("---")

	orders = db.list_orders(a["user_id"]) or []

	# Filtro por cliente
	filter_client = st.selectbox(
		"Filtrar por cliente",
		["Todos"] + list(client_options.keys()) if client_options else ["Todos"],
	)
	if filter_client != "Todos" and client_options:
		orders = [o for o in orders if o["client_id"] == client_options[filter_client]]

	if not orders:
		st.info("Sem encomendas registradas.")
		return

	for o in orders:
		cols = st.columns([0.15, 0.15, 0.15, 0.15, 0.12, 0.14, 0.14])
		with cols[0]:
			st.write(f"👤 {o['client_name']}")
		with cols[1]:
			st.write(f"Sabor: {o['flavor']}")
		with cols[2]:
			st.caption(f"Entrega: {o['due_date']}")
		with cols[3]:
			st.caption(f"Preço: R$ {o['price'] if o['price'] is not None else '-'}")
		with cols[4]:
			new_status = st.selectbox("Status", STATUS_OPTIONS, index=STATUS_OPTIONS.index(o["status"]), key=f"st_{o['id']}")
		with cols[5]:
			if st.button("💾 Salvar", key=f"save_{o['id']}"):
				if new_status != o["status"]:
					db.update_order_status(a["user_id"], o["id"], new_status)
					st.success("Status atualizado.")
					st.rerun()
		with cols[6]:
			if st.button("🗑️ Excluir", key=f"delete_{o['id']}", type="secondary"):
				# Confirmar antes de deletar
				if st.session_state.get(f"confirm_delete_order_{o['id']}", False):
					db.delete_order(a["user_id"], o["id"])
					st.success(f"Encomenda de {o['client_name']} excluída!")
					st.session_state[f"confirm_delete_order_{o['id']}"] = False
					st.rerun()
				else:
					st.session_state[f"confirm_delete_order_{o['id']}"] = True
					st.warning("Clique novamente para confirmar a exclusão")
					st.rerun()
		
		# Mostrar confirmação se necessário
		if st.session_state.get(f"confirm_delete_order_{o['id']}", False):
			st.error("⚠️ Clique novamente no botão Excluir para confirmar")
		
		st.divider()


if __name__ == "__main__":
	main()
