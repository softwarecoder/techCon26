import os
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI  # Changed this
from ai_agent.prompts import SYSTEM_PROMPT, USER_CONTEXT_TEMPLATE

class AIAgent:
    def __init__(self, google_api_key=None):
        """
        Initializes the agent with Google Gemini.
        :param google_api_key: Your Google AI Studio API Key.
        """
        self.api_key = google_api_key
        # We use local embeddings (Free) so we don't need extra API calls for the Vector DB
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_db = None
        self.llm = None

        if google_api_key:
            # Using gemini-1.5-flash (it's faster and cheaper/free for most POCs)
            # You can also use 'gemini-1.5-pro' for more complex reasoning
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-3.6-flash", 
                google_api_key=self.api_key,
                temperature=0.3 # Lower temperature = more factual/less creative
            )
        else:
            print("⚠️ WARNING: No Google API Key provided. Running in MOCK MODE.")

    def setup_knowledge_base(self, file_path):
        """Loads the text file, splits it, and stores it in a local Vector DB."""
        if not os.path.exists(file_path):
            print(f"❌ Error: {file_path} not found.")
            return

        loader = TextLoader(file_path)
        documents = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        docs = text_splitter.split_documents(documents)
        
        # Create the Vector Store (ChromaDB)
        self.vector_db = Chroma.from_documents(
            documents=docs, 
            embedding=self.embeddings,
            persist_directory="./chroma_db"
        )
        print("✅ Google Gemini RAG Knowledge base initialized.")

    def _get_relevant_knowledge(self, query):
        """Searches the Vector DB for relevant coaching tips."""
        if self.vector_db:
            # Search for the 2 most relevant snippets from your manual
            docs = self.vector_db.similarity_search(query, k=2)
            return "\n".join([d.page_content for d in docs])
        return "No specific coaching manual available."

    def chat(self, user_query, financial_summary):
        """
        The main RAG loop.
        financial_summary: A dict containing the processed engine data.
        """
        # 1. Retrieve coaching knowledge from the Vector DB
        knowledge = self._get_relevant_knowledge(user_query)

        # 2. Construct the Augmented Prompt
        # We combine the System Prompt + Knowledge + User Data + The Question
        full_prompt = USER_CONTEXT_TEMPLATE.format(
            fhs_score=financial_summary['fhs_score'],
            current_balance=financial_summary['current_balance'],
            predicted_balance=financial_summary['predicted_balance'],
            debt_status=financial_summary['debt_status'],
            top_category=financial_summary['top_category'],
            user_query=user_query
        )

        # Final payload sent to Gemini
        final_input = f"{SYSTEM_PROMPT}\n\nRELEVANT COACHING KNOWLEDGE:\n{knowledge}\n\n{full_prompt}"

        # 3. Generate Response
        if self.llm:
            try:
                # Gemini via LangChain
                response = self.llm.invoke(final_input)
                return response.content
            except Exception as e:
                return f"❌ AI Error: {str(e)}"
        else:
            # MOCK MODE logic for testing without API key
            return f"[MOCK Gemini Response] I see your score is {financial_summary['fhs_score']}. Based on your {financial_summary['top_category']} spending, I recommend using the Snowball method to clear your debt."
