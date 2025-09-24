import streamlit as st
import hashlib
import time


def inject_css():
    """Injeta o arquivo CSS personalizado em todas as páginas"""
    try:
        with open("assets/styles.css", "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass


def inject_session_persistence():
    """Injeta JavaScript para persistir a sessão e controlar sidebar"""
    js_code = """
    <script>
    // Função para salvar dados da sessão
    function saveSession(authData) {
        if (authData && authData.is_authenticated) {
            localStorage.setItem('streamlit_auth_session', JSON.stringify({
                ...authData,
                timestamp: Date.now()
            }));
        } else {
            localStorage.removeItem('streamlit_auth_session');
        }
    }
    
    // Função para carregar dados da sessão
    function loadSession() {
        try {
            const saved = localStorage.getItem('streamlit_auth_session');
            if (saved) {
                const data = JSON.parse(saved);
                // Verificar se a sessão não expirou (24 horas)
                if (Date.now() - data.timestamp < 24 * 60 * 60 * 1000) {
                    return data;
                } else {
                    localStorage.removeItem('streamlit_auth_session');
                }
            }
        } catch (e) {
            localStorage.removeItem('streamlit_auth_session');
        }
        return null;
    }
    
    // Função para controlar visibilidade da sidebar
    function toggleSidebar() {
        const sidebar = document.querySelector('section[data-testid="stSidebar"]');
        const specificSection = document.querySelector('#root > div:nth-child(1) > div.withScreencast > div > div > section');
        const welcomeText = document.querySelector('.stMarkdown:contains("Bem-vindo(a)")');
        const systemText = document.querySelector('.stMarkdown:contains("Sistema de Encomendas")');
        
        // Verificar se está na página de login
        const isLoginPage = document.body.textContent.includes('Bem-vindo(a)') && 
                           !document.body.textContent.includes('Sistema de Encomendas');
        
        if (sidebar) {
            if (isLoginPage) {
                sidebar.style.display = 'none';
            } else {
                sidebar.style.display = 'block';
            }
        }
        
        if (specificSection) {
            if (isLoginPage) {
                specificSection.style.display = 'none';
            } else {
                specificSection.style.display = 'block';
            }
        }
    }
    
    // Salvar sessão e controlar sidebar quando houver mudanças
    window.addEventListener('load', function() {
        // Aguardar o Streamlit carregar
        setTimeout(() => {
            const authData = window.parent.streamlit?.session_state?.auth;
            if (authData) {
                saveSession(authData);
            }
            toggleSidebar();
        }, 2000);
    });
    
    // Observar mudanças no DOM para controlar sidebar
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                setTimeout(toggleSidebar, 500);
            }
        });
    });
    
    // Iniciar observação
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    </script>
    """
    st.markdown(js_code, unsafe_allow_html=True)


def ensure_auth():
    """Verifica se o usuário está autenticado"""
    if "auth" not in st.session_state or not st.session_state.auth.get("is_authenticated"):
        st.warning("Faça login para acessar esta página.")
        st.stop()


def ensure_superuser():
    """Verifica se o usuário é superusuário"""
    ensure_auth()
    if not st.session_state.auth.get("is_superuser"):
        st.error("Acesso restrito aos superusuários.")
        st.stop()


def logout_button():
    """Botão de logout na sidebar"""
    if st.sidebar.button("Sair", use_container_width=True):
        st.session_state.auth = {
            "is_authenticated": False,
            "user_id": None,
            "username": None,
            "is_superuser": False,
            "bakery_name": None,
        }
        st.rerun()


def sidebar_nav():
    """Menu de navegação da sidebar"""
    a = st.session_state.auth
    
    # Adicionar opção de remover usuários para superusuários
    if a["is_superuser"]:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🔧 Administração")
        if st.sidebar.button("🗑️ Remover Usuários", use_container_width=True):
            st.switch_page("pages/3_Admin.py")
    
    logout_button()
