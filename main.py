"""
Financial RAG System with Agent Capabilities
A focused system for answering financial questions about Google, Microsoft, and NVIDIA
using their 10-K filings with query decomposition and multi-step reasoning.
"""

import os
import json
import warnings
warnings.filterwarnings("ignore")

from rag.system import FinancialRAGSystem


def main():
    """Main execution function"""
    # Set up API key from environment (do not hardcode)
    groq_api_key = os.getenv('GROQ_API_KEY')
    if not groq_api_key:
        print("Please set GROQ_API_KEY environment variable")
        print("Get a free API key from: https://console.groq.com/")
        return
    
    # Initialize system
    rag_system = FinancialRAGSystem(groq_api_key)
    
    # Setup (this will take a few minutes)
    rag_system.setup_system()
    
    # Run sample queries
    print("\n" + "="*60)
    print("RUNNING SAMPLE QUERIES")
    print("="*60)
    
    results = rag_system.run_sample_queries()
    
    # Save results
    with open('sample_results.json', 'w') as f:
        json.dump([{
            'query': r.query,
            'answer': r.answer,
            'reasoning': r.reasoning,
            'sub_queries': r.sub_queries,
            'sources': r.sources
        } for r in results], f, indent=2)
    
    print(f"\n✅ Results saved to sample_results.json")
    
    # Optional interactive mode (set NON_INTERACTIVE=1 to skip)
    if os.getenv('NON_INTERACTIVE') != '1':
        print("\n" + "="*60)
        print("INTERACTIVE MODE - Enter your questions!")
        print("Type 'quit' to exit")
        print("="*60)
        
        while True:
            user_query = input("\n🔍 Your question: ").strip()
            if user_query.lower() in ['quit', 'exit', 'q']:
                break
            
            if user_query:
                result = rag_system.query(user_query)
                print(f"\n💡 Answer: {result.answer}")
                print(f"\n🔧 Reasoning: {result.reasoning}")
                if len(result.sub_queries) > 1:
                    print(f"\n📋 Sub-queries: {', '.join(result.sub_queries)}")


if __name__ == "__main__":
    main()
