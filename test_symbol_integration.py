"""
Test Symbol Database Integration
Verify that both AngelOne and Fyers use the same centralized database
"""
import os
os.environ["DATABASE_URL"] = "sqlite:///./best_option.db"

from database.symbol import SymToken, db_session, init_db
from database.symbol_db import get_cache, load_cache_for_broker, get_symbol_count

def test_database_connection():
    """Test that database connection works"""
    print("Testing database connection...")
    init_db()
    count = get_symbol_count()
    print(f"✅ Database connected. Total symbols: {count}")
    return count > 0

def test_symbol_query():
    """Test querying symbols from database"""
    print("\nTesting symbol query...")
    
    # Query first 5 symbols
    symbols = SymToken.query.limit(5).all()
    
    if symbols:
        print(f"✅ Found {len(symbols)} symbols:")
        for sym in symbols:
            print(f"  - {sym.symbol} ({sym.exchange}) -> Token: {sym.token}")
        return True
    else:
        print("❌ No symbols found in database")
        return False

def test_cache_loading():
    """Test loading symbols into cache"""
    print("\nTesting cache loading...")
    
    cache = get_cache()
    
    # Load cache for angelone (or fyers if angelone symbols not present)
    success = load_cache_for_broker("angelone")
    
    if success:
        stats = cache.get_cache_info()
        print(f"✅ Cache loaded successfully")
        print(f"  - Total symbols: {stats['total_symbols']}")
        print(f"  - Memory usage: {stats['stats']['memory_usage_mb']}")
        print(f"  - Cache valid: {stats['cache_valid']}")
        return True
    else:
        print("❌ Failed to load cache")
        return False

def test_symbol_lookup():
    """Test symbol lookup from cache"""
    print("\nTesting symbol lookup...")
    
    from database.symbol_db import get_token, get_symbol
    
    # Get first symbol from database
    first_symbol = SymToken.query.first()
    
    if not first_symbol:
        print("❌ No symbols in database to test")
        return False
    
    # Test token lookup
    token = get_token(first_symbol.symbol, first_symbol.exchange)
    
    if token == first_symbol.token:
        print(f"✅ Token lookup successful: {first_symbol.symbol} -> {token}")
    else:
        print(f"❌ Token lookup failed")
        return False
    
    # Test symbol lookup
    symbol = get_symbol(token, first_symbol.exchange)
    
    if symbol == first_symbol.symbol:
        print(f"✅ Symbol lookup successful: {token} -> {symbol}")
        return True
    else:
        print(f"❌ Symbol lookup failed")
        return False

def test_search():
    """Test symbol search"""
    print("\nTesting symbol search...")
    
    from database.symbol_db import search_symbols
    
    # Search for NIFTY
    results = search_symbols("NIFTY", limit=5)
    
    if results:
        print(f"✅ Search successful. Found {len(results)} results:")
        for r in results[:3]:
            print(f"  - {r['symbol']} ({r['exchange']})")
        return True
    else:
        print("❌ Search returned no results")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Symbol Database Integration Test")
    print("=" * 60)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Symbol Query", test_symbol_query),
        ("Cache Loading", test_cache_loading),
        ("Symbol Lookup", test_symbol_lookup),
        ("Symbol Search", test_search),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} failed with error: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Symbol database integration is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")

if __name__ == "__main__":
    main()
