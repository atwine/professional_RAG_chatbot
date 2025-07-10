"""
Test script for evaluating retrieval quality with sample health-related queries.
"""
import os
import sys
import logging
from typing import List, Dict, Any

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from services.vector_store import VectorStoreService
from services.query_processor import QueryProcessor
from config import config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RetrievalTester:
    """Class for testing retrieval quality with sample queries."""
    
    def __init__(self):
        """Initialize the retrieval tester."""
        self.vector_store = VectorStoreService()
        self.query_processor = QueryProcessor()
        
        # Sample health-related queries for testing
        self.test_queries = [
            "What are the benefits of regular exercise?",
            "How does diet affect heart health?",
            "What are common symptoms of stress?",
            "How important is sleep for mental health?",
            "What are preventive measures for heart disease?",
            "How to maintain a balanced diet?",
            "What are the effects of vitamin deficiency?",
            "How does meditation help with anxiety?",
            "What are the risks of high blood pressure?",
            "How to improve cardiovascular health?"
        ]
        
        logger.info("Retrieval tester initialized")
    
    def run_tests(self, n_results: int = 3):
        """
        Run retrieval tests with sample queries.
        
        Args:
            n_results: Number of results to retrieve for each query.
        """
        print("\n" + "="*80)
        print(f"RUNNING RETRIEVAL TESTS WITH {len(self.test_queries)} SAMPLE QUERIES")
        print("="*80)
        
        all_results = []
        
        for i, query in enumerate(self.test_queries):
            print(f"\n\nTEST QUERY {i+1}: '{query}'")
            print("-" * 60)
            
            # Preprocess the query
            processed_query, metadata = self.query_processor.preprocess_query(query)
            
            # Log preprocessing results
            print(f"Processed Query: '{processed_query}'")
            if metadata["changes"]:
                print(f"Processing Changes: {', '.join(metadata['changes'])}")
            
            # Skip invalid queries
            if not metadata["valid"]:
                print(f"SKIPPED: {metadata['error']}")
                continue
            
            # Extract health entities
            entities = self.query_processor.extract_health_entities(processed_query)
            if entities:
                print(f"Health Entities: {', '.join(entities)}")
            
            # Get relevant context
            try:
                results = self.vector_store.get_relevant_context(processed_query, n_results=n_results)
                
                # Store results for later analysis
                all_results.append({
                    "query": query,
                    "processed_query": processed_query,
                    "results": results
                })
                
                # Print results
                print(f"\nFound {len(results)} results:")
                for j, result in enumerate(results):
                    print(f"\nResult {j+1}:")
                    print(f"Text: {result['text']}")
                    print(f"Citation: {result['citation']}")
                    print(f"Confidence: {result['confidence']}")
                    
                    # Print metadata if available
                    if result['metadata']:
                        print("Metadata:")
                        for key, value in result['metadata'].items():
                            print(f"  {key}: {value}")
            
            except Exception as e:
                logger.error(f"Error retrieving results for query '{query}': {e}")
                print(f"ERROR: {e}")
        
        print("\n" + "="*80)
        print("RETRIEVAL TESTS COMPLETED")
        print("="*80)
        
        return all_results
    
    def evaluate_results(self, results: List[Dict[str, Any]]):
        """
        Evaluate retrieval results.
        
        Args:
            results: List of retrieval results.
        """
        if not results:
            print("No results to evaluate")
            return
        
        total_queries = len(results)
        queries_with_results = sum(1 for r in results if r["results"])
        total_results = sum(len(r["results"]) for r in results)
        avg_results_per_query = total_results / total_queries if total_queries > 0 else 0
        avg_confidence = sum(result["confidence"] for r in results for result in r["results"]) / total_results if total_results > 0 else 0
        
        print("\n" + "="*80)
        print("RETRIEVAL EVALUATION")
        print("="*80)
        print(f"Total Queries: {total_queries}")
        print(f"Queries with Results: {queries_with_results} ({queries_with_results/total_queries*100:.1f}%)")
        print(f"Total Results: {total_results}")
        print(f"Average Results per Query: {avg_results_per_query:.2f}")
        print(f"Average Confidence: {avg_confidence:.4f}")
        print("="*80)


def add_sample_documents():
    """Add sample health-related documents to the vector store if it's empty."""
    vector_store = VectorStoreService()
    
    try:
        # Check if the collection is empty
        count = vector_store.collection.count()
        if count == 0:
            # Add sample documents for testing
            texts = [
                "Regular exercise can help improve cardiovascular health and reduce the risk of heart disease. It strengthens the heart muscle, lowers blood pressure, and improves circulation.",
                "A balanced diet rich in fruits, vegetables, whole grains, and lean proteins provides essential nutrients for overall health. Limiting processed foods, saturated fats, and added sugars can help prevent chronic diseases.",
                "Adequate sleep is crucial for mental health and cognitive function. During sleep, the brain processes emotions, consolidates memories, and clears waste products. Chronic sleep deprivation is linked to depression, anxiety, and impaired decision-making.",
                "Stress management techniques like meditation, deep breathing, and mindfulness can help reduce anxiety and improve well-being. Regular practice can lower stress hormones and improve emotional regulation.",
                "Regular health check-ups can help detect potential health issues early. Preventive screenings for blood pressure, cholesterol, and cancer can identify problems before they become serious.",
                "Staying hydrated is essential for bodily functions including digestion, nutrient absorption, and temperature regulation. Adults should aim for 8-10 glasses of water daily, more during exercise or hot weather.",
                "Vitamin D deficiency is common and can lead to bone problems, fatigue, and weakened immunity. The body produces vitamin D when skin is exposed to sunlight, but supplements may be necessary in winter or for those with limited sun exposure.",
                "High blood pressure, or hypertension, often has no symptoms but can lead to heart attack, stroke, and kidney damage if left untreated. Regular monitoring and lifestyle changes are key to management.",
                "Maintaining a healthy weight through diet and exercise reduces the risk of diabetes, heart disease, and certain cancers. Even modest weight loss can have significant health benefits for those who are overweight.",
                "Mental health is as important as physical health. Seeking help for depression, anxiety, or other mental health concerns is a sign of strength, not weakness. Effective treatments include therapy, medication, and lifestyle changes."
            ]
            
            metadatas = [
                {"source": "Health Guidelines", "topic": "exercise", "page": 1, "title": "Cardiovascular Benefits of Exercise", "author": "Dr. Smith"},
                {"source": "Nutrition Handbook", "topic": "diet", "page": 15, "title": "Principles of Balanced Nutrition", "author": "Dr. Johnson"},
                {"source": "Sleep Research Journal", "topic": "sleep", "page": 7, "title": "Sleep and Mental Health Connection", "author": "Dr. Williams"},
                {"source": "Mental Health Resources", "topic": "stress", "page": 22, "title": "Effective Stress Management Techniques", "author": "Dr. Brown"},
                {"source": "Preventive Care Guide", "topic": "check-ups", "page": 3, "title": "Importance of Regular Health Screenings", "author": "Dr. Davis"},
                {"source": "Hydration Science", "topic": "hydration", "page": 12, "title": "Water and Body Function", "author": "Dr. Miller"},
                {"source": "Vitamin Research", "topic": "vitamins", "page": 45, "title": "Understanding Vitamin D", "author": "Dr. Wilson"},
                {"source": "Cardiovascular Health", "topic": "blood pressure", "page": 28, "title": "Hypertension: The Silent Killer", "author": "Dr. Taylor"},
                {"source": "Weight Management", "topic": "weight", "page": 17, "title": "Health Benefits of Weight Control", "author": "Dr. Anderson"},
                {"source": "Mental Wellness Guide", "topic": "mental health", "page": 5, "title": "Prioritizing Psychological Wellbeing", "author": "Dr. Thomas"}
            ]
            
            vector_store.add_documents(texts, metadatas)
            print("[INFO] Added sample health documents to the vector store")
        else:
            print(f"[INFO] Collection already contains {count} documents")
    
    except Exception as e:
        logger.error(f"Error adding sample documents: {e}")
        print(f"[ERROR] Failed to add sample documents: {e}")


if __name__ == "__main__":
    # Add sample documents if needed
    add_sample_documents()
    
    # Run retrieval tests
    tester = RetrievalTester()
    results = tester.run_tests(n_results=3)
    
    # Evaluate results
    tester.evaluate_results(results)
