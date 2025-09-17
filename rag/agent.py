from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import json

from .chunker import Document
from .vectorstore import VectorStore


@dataclass
class QueryResult:
    query: str
    answer: str
    reasoning: str
    sub_queries: List[str]
    sources: List[Dict[str, Any]]


class QueryAgent:
    """Agent for query decomposition and multi-step reasoning"""

    def __init__(self, vector_store: VectorStore, llm_client):
        self.vector_store = vector_store
        self.llm_client = llm_client

    def _needs_decomposition(self, query: str) -> bool:
        indicators = [
            "compare", "comparison", "versus", "vs", "which", "highest", "lowest",
            "growth", "change", "difference", "all three", "across companies",
            "from", "to", "between", "how much", "what percentage"
        ]
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in indicators)

    def _decompose_query(self, query: str) -> List[str]:
        prompt = f"""
        Break down this financial query into specific sub-queries that can be answered independently.
        Each sub-query should be for a specific company and metric.

        Query: {query}

        Return only a JSON list of sub-queries, nothing else.
        Example format: ["Microsoft total revenue 2023", "Google total revenue 2023"]
        """
        try:
            response = self.llm_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=200
            )
            content = response.choices[0].message.content.strip()
            if content.startswith('[') and content.endswith(']'):
                return json.loads(content)
            lines = content.split('\n')
            cleaned = []
            for line in lines:
                if line.strip() and not line.strip().startswith('#'):
                    cleaned.append(line.strip().strip('"').strip("'"))
            return cleaned[:6]
        except Exception as e:
            print(f"Error in query decomposition: {e}")
            return [query]

    def _retrieve_for_query(self, query: str, k: int = 3):
        return self.vector_store.search(query, k=k)

    def _synthesize_answer(self, query: str, sub_queries: List[str], all_results: List[List[Tuple[Document, float]]]) -> Dict[str, Any]:
        context_parts: List[str] = []
        sources: List[Dict[str, Any]] = []
        for sub_query, results in zip(sub_queries, all_results):
            context_parts.append(f"\n--- Results for: {sub_query} ---")
            for doc, score in results:
                context_parts.append(f"[{doc.company} {doc.year}]: {doc.content[:500]}...")
                sources.append({
                    "company": doc.company,
                    "year": doc.year,
                    "excerpt": doc.content[:200] + "...",
                    "chunk_id": doc.chunk_id,
                    "relevance_score": score
                })
        context = '\n'.join(context_parts)
        prompt = f"""
        Based on the following financial document excerpts, provide a comprehensive answer to the query.
        Be specific with numbers and cite the companies/years when mentioning figures.

        Query: {query}

        Context:
        {context[:4000]}

        Provide a detailed, factual answer based only on the information in the context.
        If you cannot find specific information, state that clearly.
        """
        try:
            response = self.llm_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=500
            )
            answer = response.choices[0].message.content.strip()
            reasoning = f"Executed {len(sub_queries)} sub-queries: {', '.join(sub_queries)}. Retrieved and analyzed relevant sections from SEC filings to provide comparative analysis."
            return {
                "query": query,
                "answer": answer,
                "reasoning": reasoning,
                "sub_queries": sub_queries,
                "sources": sources[:10]
            }
        except Exception as e:
            print(f"Error in answer synthesis: {e}")
            return {
                "query": query,
                "answer": f"Error generating answer: {e}",
                "reasoning": "Error in synthesis step",
                "sub_queries": sub_queries,
                "sources": sources[:5]
            }

    def process_query(self, query: str) -> QueryResult:
        print(f"\n=== Processing Query: {query} ===")
        if self._needs_decomposition(query):
            print("Query needs decomposition...")
            sub_queries = self._decompose_query(query)
            print(f"Sub-queries: {sub_queries}")
            all_results = []
            for sub_query in sub_queries:
                results = self._retrieve_for_query(sub_query, k=3)
                all_results.append(results)
                print(f"Retrieved {len(results)} results for: {sub_query}")
            result_dict = self._synthesize_answer(query, sub_queries, all_results)
        else:
            print("Simple query, direct retrieval...")
            results = self._retrieve_for_query(query, k=5)
            if results:
                context = '\n'.join([f"[{doc.company} {doc.year}]: {doc.content[:300]}..." for doc, score in results])
                prompt = f"""
                Answer this financial question based on the provided context.
                Be specific and cite companies/years for any numbers mentioned.

                Question: {query}
                Context: {context}

                Provide a direct, factual answer.
                """
                try:
                    response = self.llm_client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.1,
                        max_tokens=300
                    )
                    answer = response.choices[0].message.content.strip()
                except Exception as e:
                    answer = f"Error generating answer: {e}"
                result_dict = {
                    "query": query,
                    "answer": answer,
                    "reasoning": "Direct retrieval from vector store with single-step reasoning",
                    "sub_queries": [query],
                    "sources": [{
                        "company": doc.company,
                        "year": doc.year,
                        "excerpt": doc.content[:200] + "...",
                        "chunk_id": doc.chunk_id,
                        "relevance_score": score
                    } for doc, score in results[:5]]
                }
            else:
                result_dict = {
                    "query": query,
                    "answer": "No relevant information found in the vector store.",
                    "reasoning": "No matching documents found",
                    "sub_queries": [query],
                    "sources": []
                }
        return QueryResult(**result_dict)


