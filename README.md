# Sistema de Encomendas de Bolos (Streamlit + SQLite)

Aplicativo para gerenciamento de encomendas de bolos por docerias. Suporta múltiplos usuários (docerias) e superusuários para administração.

## Requisitos

- Python 3.9+
- Pip

## Instalação

```bash
pip install -r requirements.txt
```

## Executar

```bash
streamlit run app.py
```

O sistema criará automaticamente o banco `data/app.db` e um superusuário padrão caso ainda não exista:

- Usuário: `admin`
- Senha: `admin123`

Altere a senha em `Admin` assim que possível.

## Estrutura

- `app.py`: Página inicial (Home) com destaque para pendentes e em preparação e tela de login
- `db.py`: Camada de acesso ao banco (SQLite)
- `auth.py`: Autenticação e utilitários de segurança
- `pages/1_Clientes.py`: Cadastro/Listagem/Remoção de clientes
- `pages/2_Encomendas.py`: Adicionar/Listar/Filtrar/Atualizar status de encomendas
- `pages/3_Admin.py`: Administração (alterar senha, gerenciar usuários docerias - apenas superuser)
- `.streamlit/config.toml`: Tema e estilo
- `assets/styles.css`: Estilos adicionais

## Observações

- Os dados são isolados por doceria (cada usuário vê apenas seus clientes e encomendas)
- Status de encomendas: `Pendente`, `Pago (Em preparação)`, `Entregue`
