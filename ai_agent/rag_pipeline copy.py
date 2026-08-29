import os
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_classic.chains import RetrievalQA
from ai_agent.prompts import SYSTEM_PROMPT, USER_CONTEXT_TEMPLATE

class AIAgent:
    def __init__(self, openai_api_key=None):
        self.api_key = openai_api_key
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_db = None
        self.llm = None

        if openai_api_key:
            self.llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=self.api_key)
        else:
            print("⚠️ WARNING: No OpenAI API Key provided. Running in MOCK MODE (No real AI).")

    def setup_knowledge_base(self, file_path):
        """Loads the text file, splits it, and stores it in a local Vector DB."""
        loader = TextLoader(file_path)
        documents = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        docs = text_splitter.split_documents(documents)
        
        self.vector_db = Chroma.from_documents(
            documents=docs, 
            embedding=self.embeddings,
            persist_directory="./chroma_db"
        )
        print("✅ Knowledge base initialized.")

    def _get_relevant_knowledge(self, query):
        """Searches the Vector DB for relevant coaching tips."""
        if self.vector_db:
            docs = self.vector_db.similarity_search(query, k=2)
            return "\n".join([d.page_content for d in docs])
        return "No specific coaching manual available."

    def chat(self, user_query, financial_summary):
        """
        The main RAG loop.
        financial_summary: A dict containing the processed engine data.
        """
        # 1. Retrieve coaching knowledge
        knowledge = self._get_relevant_knowledge(user_query)

        # 2. Construct the Augmented Prompt
        full_prompt = USER_CONTEXT_TEMPLATE.format(
            fhs_score=financial_summary['fhs_score'],
            current_balance=financial_summary['current_balance'],
            predicted_balance=financial_summary['predicted_balance'],
            debt_status=financial_summary['debt_status'],
            top_category=financial_summary['top_category'],
            user_query=user_query
        )

        # Combine everything
        final_input = f"{SYSTEM_PROMPT}\n\nRELEVANT COACHING KNOWLEDGE:\n{knowledge}\n\n{full_prompt}"

        # 3. Generate Response
        if self.llm:
            response = self.llm.invoke(final_input)
            return response.content
        else:
            # MOCK MODE logic for testing without API key
            return f"[MOCK AI RESPONSE] I see your score is {financial_summary['fhs_score']}. Based on your {financial_summary['top_category']} spending, I recommend using the Snowball method to clear your debt."

