pip install -r requirements.txt
import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go

# Import your custom modules
from data_generator import LATAMDataGenerator
from engine.scoring import ScoringEngine
from engine.predictor import PredictorEngine
from engine.optimizer import OptimizerEngine
from ai_agent.rag_pipeline import AIAgent

# --- PAGE CONFIG ---
st.set_page_config(page_title="Smart Banker AI", layout="wide", page_icon="💰")

# --- SESSION STATE INITIALIZATION ---
# This ensures that when the app re-runs, your chat history doesn't disappear
if "messages" not in st.session_state:
    st.session_state.messages = []
if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False

# --- SIDEBAR: CONFIGURATION & DATA CONTROL ---
with st.sidebar:
    st.title("⚙️ Control Panel")
    st.subheader("Data Management")
    locale = st.selectbox("Select Region", ["pt_BR (Brazil)", "es_MX (Mexico)"])
    
    if st.button("🔄 Regenerate New User Data"):
        loc = 'pt_BR' if 'pt_BR' in locale else 'es_MX'
        gen = LATAMDataGenerator(locale=loc)
        user = gen.generate_user_profile()
        df = gen.generate_transactions(days_back=90)
        debt = gen.generate_debt_data()
        
        # Save files
        df.to_csv("user_transactions.csv", index=False)
        with open("user_profile.json", "w") as f:
            json.dump({"profile": user, "debt": debt}, f)
        
        st.session_state.data_loaded = True
        st.rerun()

    st.divider()
    st.subheader("AI Settings")
    api_key = st.text_input("Enter  API Key", type="password")
    st.info("Without an API key, the AI will run in 'Mock Mode'.")

# --- MAIN CONTENT ---
st.title("💰 Smart Banker: AI Financial Coach")

if not st.session_state.data_loaded:
    st.warning("👈 Please click 'Regenerate New User Data' in the sidebar to start.")
    st.stop()

# --- 1. LOAD DATA ---
df = pd.read_csv("user_transactions.csv", parse_dates=['date'])
with open("user_profile.json", "r") as f:
    raw_data = json.load(f)
user_profile = raw_data['profile']
debt_info = raw_data['debt']

# --- 2. RUN ENGINES ---
with st.spinner("Analyzing your finances..."):
    # Scoring
    scoring_results = ScoringEngine(df, debt_info, user_profile).calculate_fhs()
    # Prediction
    prediction_results = PredictorEngine(df).predict_cash_flow()
    # Optimization
    debt_results = OptimizerEngine(debt_info).get_debt_recommendations()
    
    # Prepare Summary for AI Agent
    ai_context = {
        "fhs_score": scoring_results['final_score'],
        "current_balance": prediction_results['current_balance'],
        "predicted_balance": prediction_results['predicted_balance_30d'],
        "debt_status": f"Total Debt: {debt_results['total_debt']}",
        "top_category": df[df['type'] == 'Expense'].groupby('category')['amount'].sum().abs().idxmax()
    }

# --- 3. DASHBOARD UI ---

# ROW 1: KPI Metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Financial Health Score", f"{scoring_results['final_score']}/100", 
              delta=f"{scoring_results['breakdown']['savings_score']}% Savings Power", delta_color="normal")
with col2:
    st.metric("Current Balance", f"{user_profile['currency']} {prediction_results['current_balance']:,}")
with col3:
    st.metric("30-Day Forecast", f"{user_profile['currency']} {prediction_results['predicted_balance_30d']:,}",
              delta=f"{prediction_results['trend_slope']} trend", delta_color="inverse")
with col4:
    st.metric("Total Debt", f"{user_profile['currency']} {debt_results['total_debt']:,}", delta_color="inverse")

st.divider()

# ROW 2: Visualizations
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📈 Cash Flow Trend")
    # Create balance line chart
    df['cumulative_balance'] = df['amount'].cumsum()
    fig_line = px.line(df, x='date', y='cumulative_balance', title="Historical Balance")
    st.plotly_chart(fig_line, use_container_width=True)

with col_right:
    st.subheader("📊 Spending by Category")
    expense_df = df[df['type'] == 'Expense'].copy()
    expense_df['amount'] = expense_df['amount'].abs()
    fig_pie = px.pie(expense_df, values='amount', names='category', hole=0.4)
    st.plotly_chart(fig_pie, use_container_width=True)

st.divider()

# ROW 3: Intelligence & AI Coach
col_intel, col_chat = st.columns([1, 1.5])

with col_intel:
    st.subheader("🛡️ Debt Rescue Plan")
    st.write("**Snowball Method (Smallest First):**")
    st.info(debt_results['strategies']['snowball_order'])
    
    st.write("**Avalanche Method (Highest Interest):**")
    st.info(debt_results['strategies']['avalanche_order'])
    
    st.warning(f"**Refinance Advice:** {debt_results['refinance_recommendation']}")

with col_chat:
    st.subheader("🤖 Chat with your AI Coach")
    
    # Initialize AI Agent
    #agent = AIAgent(openai_api_key=api_key)
    agent = AIAgent(google_api_key=api_key) # Update this name
    agent.setup_knowledge_base("financial_knowledge.txt")

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input
    if prompt := st.chat_input("Ask me about your spending, debt, or savings..."):
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = agent.chat(prompt, ai_context)
                st.markdown(response)
        
        # Add assistant message to history
        st.session_state.messages.append({"role": "assistant", "content": response})
