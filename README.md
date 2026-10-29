# 💰 Meu Financeiro - Controle de Gastos Pessoais (Django)

![Badge Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![Badge Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Badge Bootstrap](https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white)
![Badge Status](https://img.shields.io/badge/Status-Em_Desenvolvimento-brightgreen?style=for-the-badge)

Um sistema de gestão financeira pessoal completo, construído do zero com **Python/Django** e uma interface inspirada em **Bullet Journal** (visual de caderno de planejamento). O objetivo é ser uma ferramenta prática para o controle de gastos familiares, projeções futuras e automação de faturas de cartão de crédito.

## ✨ Funcionalidades

### 📅 Gestão de Meses e Lançamentos
- **Abertura e Fechamento de Meses:** Controle o mês ativo e feche os meses quando eles acabarem.
- **Clonagem de Mês:** Copie as receitas e gastos fixos do mês anterior para o novo mês com um clique.
- **Receitas e Gastos:** Lançamentos manuais com categorização, pessoa (quem gastou) e formas de pagamento.
- **Parcelamento Inteligente:** Lançamento de compras parceladas com controle de parcela atual e total. O sistema projeta as parcelas automaticamente nos meses futuros.

### 💳 Cartões e Faturas
- **Cadastro de Cartões:** Com limite, dia de vencimento e cor personalizada para o card.
- **Importação de Faturas em PDF:** Leitor automático de PDFs do **Nubank** e **Santander**.
  - Extração inteligente de transações, valores e parcelas.
  - Tratamento de "lixo" no PDF (como pagamentos e totais).
  - Distribuição automática de parcelas futuras para os próximos meses.

### 📊 Dashboard e Relatórios
- **Tela Inicial (Home):** 
  - Painel de resumo rápido (Gastos, Receitas e Saldo Livre).
  - Cards de faturas de cartão com as cores dos bancos.
  - Cards de contas individuais com cores personalizadas por categoria.
  - Calendário interativo com os vencimentos do mês.
  - Extrato completo do mês.
  - **Modo Privacidade:** Efeito de desfoque (blur) nos valores para segurança em locais públicos.
- **Dashboard Analítico:**
  - Gráfico de rosca com a divisão de gastos por categoria.
  - Método 50-30-20 (Essenciais, Não Essenciais e Sobra).
  - Acompanhamento de orçamentos por categoria com barras de progresso.
- **Projeção de 12 Meses:** 
  - Visão mês a mês de todas as parcelas futuras.
  - Cálculo de Saldo Livre (Receitas - Gastos).
  - Navegação pelo futuro sem alterar o mês ativo do sistema.
- **Relatórios Inteligentes:**
  - Top 5 maiores gastos do mês.
  - Divisão de gastos por pessoa (Quem gastou o quê).
  - Média de gastos dos últimos 3 meses.
  - Dicas de economia geradas automaticamente com base nos dados.
  - **Exportação para Excel:** Baixe o relatório com gráficos nativos e formatação condicional.

### 🔐 Segurança e Personalização
- **Autenticação:** Login e Logout seguros (Django Auth).
- **Perfil do Usuário:** Upload de foto de perfil e alteração de senha.
- **Cofre:** Gestão de dívidas (com juros) e Reserva de Emergência.
- **Histórico:** Consulta de meses já fechados.

---

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python 3, Django 5
- **Frontend:** HTML5, CSS3, Bootstrap 5, JavaScript
- **Gráficos:** Chart.js, FullCalendar (Calendário)
- **Leitura de PDF:** pdfplumber, Regex
- **Excel:** openpyxl
- **Banco de Dados:** SQLite (Desenvolvimento)

---

## 🚀 Como Rodar o Projeto Localmente

### Pré-requisitos
- Python 3.10+
- Git

### Passo a Passo

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/seu-usuario/controle_financeiro.git
   cd controle_financeiro