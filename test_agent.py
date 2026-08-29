from ai_agent.rag_pipeline import AIAgent

# 1. Setup Dummy Financial Data (In reality, this comes from your engines)
dummy_summary = {
    "fhs_score": 62,
    "current_balance": 1200.50,
    "predicted_balance": -150.00,  # User is going broke!
    "debt_status": "High ($5,000 total)",
    "top_category": "Food & Entertainment"
}

# 2. Initialize Agent
# Replace 'your-api-key' with your actual OpenAI key to see real magic
agent = AIAgent(openai_api_key=None) 

# 3. Load Knowledge Base
agent.setup_knowledge_base("financial_knowledge.txt")

# 4. Test a question
print("\n--- Testing AI Voice ---")
query = "Can I afford to buy a new iPhone this month?"
response = agent.chat(query, dummy_summary)

print(f"Question: {query}")
print(f"Smart Banker: {response}")
