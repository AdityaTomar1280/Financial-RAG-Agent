import os
from typing import Optional
from groq import Groq

from .sec_data import SECDataAcquisition
from .chunker import TextChunker
from .vectorstore import VectorStore
from .agent import QueryAgent, QueryResult


class FinancialRAGSystem:
    """Main RAG system orchestrator"""

    def __init__(self, groq_api_key: Optional[str] = None):
        self.data_acquisition = SECDataAcquisition()
        self.chunker = TextChunker()
        self.vector_store = VectorStore()

        effective_api_key = groq_api_key or os.getenv('GROQ_API_KEY')
        if not effective_api_key:
            raise RuntimeError("GROQ_API_KEY is not set. Please export GROQ_API_KEY in your environment.")
        self.llm_client = Groq(api_key=effective_api_key)

        self.agent = QueryAgent(self.vector_store, self.llm_client)

    def setup_system(self):
        print("=== Setting up Financial RAG System ===")
        print("\n1. Acquiring SEC filing data...")
        company_data = self.data_acquisition.acquire_all_data()

        print("\n2. Processing and chunking documents...")
        all_documents = []
        for company, years_data in company_data.items():
            for year, text in years_data.items():
                if text:
                    chunks = self.chunker.chunk_text(text, company, year, f"{company}_{year}_10K")
                    all_documents.extend(chunks)
                    print(f"Created {len(chunks)} chunks for {company} {year}")

        print(f"\n3. Building vector store with {len(all_documents)} documents...")
        self.vector_store.add_documents(all_documents)
        print("✅ System setup complete!")

    def query(self, question: str) -> QueryResult:
        return self.agent.process_query(question)

    def run_sample_queries(self):
        test_queries = [
            "What was NVIDIA's total revenue in fiscal year 2024?",
            "What percentage of Google's 2023 revenue came from advertising?",
            "How much did Microsoft's cloud revenue grow from 2022 to 2023?",
            "Which of the three companies had the highest gross margin in 2023?",
            "Compare the R&D spending as a percentage of revenue across all three companies in 2023",
        ]

        results = []
        for query in test_queries:
            result = self.query(query)
            results.append(result)
            print(f"\n{'='*50}")
            print(f"Query: {result.query}")
            print(f"Answer: {result.answer}")
            print(f"Reasoning: {result.reasoning}")
            print(f"Sub-queries: {result.sub_queries}")
            print(f"Sources: {len(result.sources)} documents")
        return results


