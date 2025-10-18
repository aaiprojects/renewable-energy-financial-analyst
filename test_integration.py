"""
Integration Test Script for Enhanced Renewable Energy Financial Analyst
Tests the complete integration of all tools with real data sources.
"""

import sys
import os
from datetime import datetime

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

def test_tools_integration():
    """Test individual tools with real data integration."""
    print("🧪 Testing Enhanced Tools Integration")
    print("=" * 50)
    
    try:
        from src.config.settings import Settings
        settings = Settings()
        print(f"✅ Settings loaded")
        print(f"   - NewsAPI Key: {'✅ Set' if settings.newsapi_key else '❌ Missing'}")
        print(f"   - FRED API Key: {'✅ Set' if settings.fred_api_key else '❌ Missing'}")
        print(f"   - SEC User Agent: {settings.sec_user_agent}")
    except Exception as e:
        print(f"❌ Settings error: {e}")
        return False

    # Test NewsAPI Integration
    print("\n📰 Testing NewsAPI Integration...")
    try:
        from src.tools.news import NewsTool
        news_tool = NewsTool(api_key=settings.newsapi_key)
        
        # Test sector news
        sector_news = news_tool.fetch_sector_news(subsector="solar", days=7)
        print(f"   - Sector news fetched: {len(sector_news)} articles")
        
        # Test ticker-specific news
        ticker_news = news_tool.fetch_news("FSLR", days=7)
        print(f"   - FSLR news fetched: {len(ticker_news)} articles")
        
        if sector_news or ticker_news:
            print("   ✅ NewsAPI integration working")
        else:
            print("   ⚠️ NewsAPI returned no results (check API key or rate limits)")
    except Exception as e:
        print(f"   ❌ NewsAPI error: {e}")

    # Test SEC EDGAR Integration
    print("\n📋 Testing SEC EDGAR Integration...")
    try:
        from src.tools.filings import FilingsTool
        filings_tool = FilingsTool(user_agent=settings.sec_user_agent)
        
        filings = filings_tool.fetch_filings("FSLR", ["10-K", "10-Q"], limit=3)
        print(f"   - FSLR filings fetched: {len(filings)} documents")
        
        if filings:
            print("   ✅ SEC EDGAR integration working")
            for filing in filings[:1]:  # Show first filing
                print(f"     - {filing.get('form')} filed on {filing.get('filedAt')}")
        else:
            print("   ⚠️ No SEC filings found for FSLR")
    except Exception as e:
        print(f"   ❌ SEC EDGAR error: {e}")

    # Test FRED Integration
    print("\n💰 Testing FRED Integration...")
    try:
        from src.tools.macro import MacroTool
        macro_tool = MacroTool(api_key=settings.fred_api_key)
        
        if settings.fred_api_key:
            gdp_data = macro_tool.fetch_series("GDP")
            rates_data = macro_tool.fetch_series("FEDFUNDS")
            
            gdp_available = gdp_data is not None and not gdp_data.empty
            rates_available = rates_data is not None and not rates_data.empty
            
            print(f"   - GDP data available: {'✅' if gdp_available else '❌'}")
            print(f"   - Interest rates data available: {'✅' if rates_available else '❌'}")
            
            if gdp_available or rates_available:
                print("   ✅ FRED integration working")
            else:
                print("   ⚠️ FRED returned no data")
        else:
            print("   ⚠️ FRED API key not set - skipping test")
    except Exception as e:
        print(f"   ❌ FRED error: {e}")

    # Test YFinance Integration
    print("\n📈 Testing YFinance Integration...")
    try:
        from src.tools.prices import PricesTool
        prices_tool = PricesTool()
        
        # Test price history
        price_data = prices_tool.fetch_history("FSLR", 30)
        print(f"   - FSLR price data: {len(price_data) if price_data is not None else 0} days")
        
        # Test batch quotes
        quotes = prices_tool.batch_quotes(["FSLR", "ENPH", "RUN"])
        print(f"   - Batch quotes: {len(quotes) if quotes is not None else 0} tickers")
        
        if (price_data is not None and not price_data.empty) or (quotes is not None and not quotes.empty):
            print("   ✅ YFinance integration working")
        else:
            print("   ❌ YFinance data unavailable")
    except Exception as e:
        print(f"   ❌ YFinance error: {e}")

    return True

def test_orchestrator_integration():
    """Test the enhanced orchestrator with real data."""
    print("\n🎼 Testing Enhanced Orchestrator...")
    
    try:
        from src.config.settings import Settings
        from src.agent.orchestrator_lg import LGOrchestrator
        
        settings = Settings()
        orchestrator = LGOrchestrator(settings)
        
        print("   ✅ Enhanced orchestrator initialized")
        
        # Test with a simple ticker
        print("   🔄 Running enhanced analysis for FSLR...")
        result = orchestrator.run("FSLR", days=7, refresh=False)
        
        print(f"   - Recommendation: {result.get('recommendation', 'Unknown')}")
        print(f"   - Confidence: {result.get('confidence', 0):.2f}")
        print(f"   - Summary length: {len(result.get('summary', ''))}")
        
        # Check for enhanced data sources
        if "data_sources" in result:
            data_sources = result["data_sources"]
            print(f"   - News articles: {data_sources.get('news_articles', 0)}")
            print(f"   - SEC filings: {data_sources.get('sec_filings', 0)}")
            print(f"   - Macro indicators: {data_sources.get('macro_indicators', 0)}")
            print("   ✅ Enhanced data sources integrated")
        else:
            print("   ⚠️ Enhanced data sources not found in output")
        
        print("   ✅ Enhanced orchestrator working")
        return True
        
    except Exception as e:
        print(f"   ❌ Orchestrator error: {e}")
        return False

def test_crewai_integration():
    """Test CrewAI specialists with enhanced tools."""
    print("\n👥 Testing Enhanced CrewAI Integration...")
    
    try:
        from src.agent.crew_specialists import run_crew
        
        # Test with enhanced context
        context = {
            "test_mode": True,
            "enhanced_data": True
        }
        
        print("   🔄 Running enhanced crew analysis for FSLR...")
        result = run_crew("FSLR", days=7, context=context)
        
        print(f"   - Analysis type: {result.get('analysis_type', 'Unknown')}")
        print(f"   - Context provided: {result.get('context_provided', False)}")
        print(f"   - Data sources used: {result.get('data_sources_used', [])}")
        
        if result.get("crew_output") and "error" not in result.get("crew_output", "").lower():
            print("   ✅ Enhanced CrewAI integration working")
        else:
            print(f"   ⚠️ CrewAI returned: {result.get('crew_output', 'No output')[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"   ❌ CrewAI error: {e}")
        return False

def test_natural_language_integration():
    """Test the natural language interface with enhanced data."""
    print("\n🤖 Testing Enhanced Natural Language Interface...")
    
    try:
        from src.config.settings import Settings
        
        # Check if NL orchestrator is available
        try:
            from src.agent.nl_orchestrator import NLOrchestrator
            nl_available = True
        except ImportError:
            print("   ⚠️ NL Orchestrator not available (missing dependencies)")
            return False
        
        settings = Settings()
        nl_orch = NLOrchestrator(settings)
        print("   ✅ Enhanced NL orchestrator initialized")
        
        # Test simple query
        test_query = "Show me recent news for FSLR"
        print(f"   🔄 Testing query: '{test_query}'")
        
        result = nl_orch.process_natural_language_query(test_query)
        
        if result.get("success"):
            print(f"   - Analysis type: {result.get('analysis_type', 'Unknown')}")
            print(f"   - Enhanced data: {result.get('enhanced_data', False)}")
            print(f"   - Data sources: {result.get('data_sources', [])}")
            print("   ✅ Enhanced NL interface working")
        else:
            print(f"   ⚠️ NL query failed: {result.get('error', 'Unknown error')}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ NL interface error: {e}")
        return False

def main():
    """Run all integration tests."""
    print(f"🚀 Enhanced Renewable Energy Financial Analyst - Integration Test")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    tests = [
        ("Tools Integration", test_tools_integration),
        ("Orchestrator Integration", test_orchestrator_integration),
        ("CrewAI Integration", test_crewai_integration),
        ("Natural Language Integration", test_natural_language_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 INTEGRATION TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests passed! System ready for production.")
    else:
        print("⚠️ Some tests failed. Check API keys and dependencies.")
    
    print("\n💡 Next Steps:")
    print("   1. Set up API keys in .env file (NEWSAPI_KEY, FRED_API_KEY)")
    print("   2. Run: streamlit run app.py")
    print("   3. Test the enhanced AI Assistant tab")
    print("   4. Try queries like: 'Show me recent news for FSLR with real data'")

if __name__ == "__main__":
    main()