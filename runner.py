import os
import json
from rag.system import FinancialRAGSystem


def main():
    groq_api_key = os.getenv('GROQ_API_KEY')
    if not groq_api_key:
        print("Please set GROQ_API_KEY environment variable")
        print("Get a free API key from: https://console.groq.com/")
        return

    rag_system = FinancialRAGSystem(groq_api_key)
    rag_system.setup_system()

    print("\n" + "="*60)
    print("RUNNING SAMPLE QUERIES")
    print("="*60)

    results = rag_system.run_sample_queries()

    with open('sample_results.json', 'w') as f:
        json.dump([{
            'query': r.query,
            'answer': r.answer,
            'reasoning': r.reasoning,
            'sub_queries': r.sub_queries,
            'sources': r.sources
        } for r in results], f, indent=2)

    print(f"\n✅ Results saved to sample_results.json")


if __name__ == "__main__":
    main()


