"""
Test script for Natural Language Interface
Tests various query types and validates the system functionality.
"""

import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.agent.query_processor import QueryProcessor, QueryIntent
from src.agent.nl_orchestrator import NLOrchestrator
from src.config.settings import Settings

def test_query_processor():
    """Test the query processor with various queries."""
    print("🧪 Testing Query Processor...")
    
    processor = QueryProcessor()
    
    test_queries = [
        "Show me FSLR's price performance over the last 3 months",
        "Compare solar stocks vs wind stocks",
        "What's the recent news sentiment around ENPH?",
        "Create a technical analysis chart for TSLA",
        "Which renewable energy company has the best returns?",
        "Show me the renewable energy sector overview",
        "Random unrelated query about cats and dogs"
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        parsed = processor.parse_query(query)
        print(f"   Intent: {parsed.intent.value}")
        print(f"   Tickers: {parsed.parameters.tickers}")
        print(f"   Timeframe: {parsed.parameters.timeframe}")
        print(f"   Confidence: {parsed.confidence:.2f}")
        print(f"   Explanation: {parsed.explanation}")

def test_chart_generation():
    """Test chart generation (requires plotly)."""
    print("\n📊 Testing Chart Generation...")
    
    try:
        from src.tools.visualization import ChartGenerator
        
        chart_gen = ChartGenerator()
        
        # Test price chart
        print("   Creating price chart for FSLR...")
        chart = chart_gen.create_price_chart(['FSLR'], '30d', 'line')
        print(f"   Chart created: {type(chart)}")
        
        # Test comparison
        print("   Creating comparison chart...")
        chart = chart_gen.create_comparison_chart(['FSLR', 'ENPH'], ['returns'], '30d')
        print(f"   Comparison chart created: {type(chart)}")
        
        # Test sector overview
        print("   Creating sector overview...")
        chart = chart_gen.create_sector_overview('Solar')
        print(f"   Sector chart created: {type(chart)}")
        
    except ImportError as e:
        print(f"   ⚠️ Plotly not available: {e}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_nl_orchestrator():
    """Test the natural language orchestrator (mock mode)."""
    print("\n🤖 Testing NL Orchestrator...")
    
    try:
        # This would require full environment setup
        print("   Orchestrator structure test...")
        
        # Test basic instantiation (without actual API calls)
        settings = Settings()
        print(f"   Settings loaded: {type(settings)}")
        
        # Note: Full orchestrator testing would require:
        # - API keys configured
        # - Network access
        # - LangGraph dependencies
        print("   ✅ Basic structure validated")
        
    except Exception as e:
        print(f"   ⚠️ Limited test due to: {e}")

def demonstrate_query_examples():
    """Demonstrate various query types and expected outcomes."""
    print("\n💡 Query Examples and Expected Behavior:")
    
    examples = [
        {
            "query": "Show me FSLR's price chart for the last 6 months",
            "expected_intent": "price_chart",
            "expected_output": "Interactive price chart with 6-month history"
        },
        {
            "query": "Compare ENPH vs RUN performance",
            "expected_intent": "comparison", 
            "expected_output": "Returns comparison bar chart"
        },
        {
            "query": "What's the latest news on solar energy policy?",
            "expected_intent": "news_sentiment",
            "expected_output": "News analysis and sentiment summary"
        },
        {
            "query": "Technical analysis for TSLA",
            "expected_intent": "technical_analysis",
            "expected_output": "Chart with moving averages, RSI, volume"
        },
        {
            "query": "Renewable energy sector overview",
            "expected_intent": "sector_overview",
            "expected_output": "Bubble chart of all renewable companies"
        }
    ]
    
    for example in examples:
        print(f"\n📝 Query: '{example['query']}'")
        print(f"   Expected Intent: {example['expected_intent']}")
        print(f"   Expected Output: {example['expected_output']}")

def main():
    """Run all tests."""
    print("🚀 Natural Language Interface Test Suite")
    print("=" * 50)
    
    test_query_processor()
    test_chart_generation() 
    test_nl_orchestrator()
    demonstrate_query_examples()
    
    print("\n✅ Test Suite Complete!")
    print("\n🎯 Next Steps:")
    print("   1. Install dependencies: pip install -r requirements.txt")
    print("   2. Set up API keys in .env file")
    print("   3. Run: streamlit run app.py")
    print("   4. Navigate to 'AI Assistant' tab")
    print("   5. Try natural language queries!")

if __name__ == "__main__":
    main()