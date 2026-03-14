import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

function Dashboard() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [masterContract, setMasterContract] = useState({
    status: 'pending',
    message: '',
    total_symbols: 0
  });
  
  // Search state
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [selectedExchange, setSelectedExchange] = useState('');

  useEffect(() => {
    // Check if user is logged in
    const userData = localStorage.getItem('user');
    if (!userData) {
      navigate('/login');
      return;
    }
    setUser(JSON.parse(userData));
    
    // Check master contract status
    checkMasterContractStatus();
    
    // Poll every 5 seconds until successful
    const interval = setInterval(() => {
      if (masterContract.status !== 'success') {
        checkMasterContractStatus();
      }
    }, 5000);
    
    return () => clearInterval(interval);
  }, [navigate]);

  const checkMasterContractStatus = async () => {
    try {
      // Get broker from logged-in user
      const userData = localStorage.getItem('user');
      if (!userData) return;
      
      const user = JSON.parse(userData);
      const broker = user.broker || 'angelone';
      
      const response = await fetch(`http://127.0.0.1:8000/api/master-contract/status?broker=${broker}`);
      if (response.ok) {
        const data = await response.json();
        setMasterContract(data);
      }
    } catch (error) {
      console.error('Failed to check master contract status:', error);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim() || searchQuery.length < 2) {
      setSearchResults([]);
      return;
    }

    setSearching(true);
    try {
      const params = new URLSearchParams({ query: searchQuery.trim() });
      if (selectedExchange) {
        params.append('exchange', selectedExchange);
      }
      
      // Add broker filter from logged-in user
      if (user && user.broker) {
        params.append('broker', user.broker);
      }

      const response = await fetch(`http://127.0.0.1:8000/api/search/symbols?${params.toString()}`);
      if (response.ok) {
        const data = await response.json();
        setSearchResults(data.data || []);
      } else {
        setSearchResults([]);
      }
    } catch (error) {
      console.error('Search failed:', error);
      setSearchResults([]);
    } finally {
      setSearching(false);
    }
  };

  const copyToClipboard = (text, type) => {
    navigator.clipboard.writeText(text)
      .then(() => alert(`${type} copied to clipboard!`))
      .catch(() => alert('Failed to copy'));
  };

  // Debounced search - trigger search after user stops typing
  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchQuery.length >= 2) {
        handleSearch();
      } else {
        setSearchResults([]);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [searchQuery, selectedExchange]);

  const getMasterContractLedColor = () => {
    switch (masterContract.status) {
      case 'success':
        return 'bg-green-500';
      case 'downloading':
        return 'bg-yellow-500 animate-pulse';
      case 'error':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getMasterContractStatusText = () => {
    switch (masterContract.status) {
      case 'success':
        return masterContract.total_symbols 
          ? `Ready (${masterContract.total_symbols} symbols)`
          : 'Ready';
      case 'downloading':
        return 'Downloading...';
      case 'error':
        return 'Error';
      default:
        return 'Pending';
    }
  };

  const getMasterContractTextColor = () => {
    switch (masterContract.status) {
      case 'success':
        return 'text-green-400';
      case 'downloading':
        return 'text-yellow-400';
      case 'error':
        return 'text-red-400';
      default:
        return 'text-gray-400';
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('user');
    localStorage.removeItem('auth_token');
    localStorage.removeItem('feed_token');
    navigate('/login');
  };

  if (!user) {
    return <div className="min-h-screen bg-gray-900 flex items-center justify-center">
      <p className="text-white">Loading...</p>
    </div>;
  }

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <header className="bg-gray-800 shadow-lg">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-white">Best-Option Dashboard</h1>
          <button
            onClick={handleLogout}
            className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded"
          >
            Logout
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* User Info Card */}
        <div className="bg-gray-800 rounded-lg p-6 mb-6">
          <div className="flex justify-between items-start">
            <div>
              <h2 className="text-xl font-semibold text-white mb-4">Welcome, {user.name}!</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-gray-300">
                <div>
                  <p className="text-gray-400">Email:</p>
                  <p className="font-semibold">{user.email}</p>
                </div>
                <div>
                  <p className="text-gray-400">Broker:</p>
                  <p className="font-semibold uppercase">{user.broker}</p>
                </div>
              </div>
            </div>
            
            {/* Master Contract Status Indicator */}
            <div className="flex items-center gap-3 bg-gray-700 rounded-lg px-4 py-3">
              <span className="text-sm font-medium text-gray-300">Master Contract:</span>
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${getMasterContractLedColor()}`} />
                <span 
                  className={`text-sm ${getMasterContractTextColor()}`}
                  title={masterContract.message}
                >
                  {getMasterContractStatusText()}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Feature Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-2">Options Chain</h3>
            <p className="text-gray-400 mb-4">Real-time options data and analytics</p>
            <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded">
              View Chain
            </button>
          </div>

          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-2">3D Visualization</h3>
            <p className="text-gray-400 mb-4">Interactive open interest maps</p>
            <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded">
              Open 3D View
            </button>
          </div>

          <div className="bg-gray-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-2">Strategies</h3>
            <p className="text-gray-400 mb-4">Build and backtest strategies</p>
            <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded">
              Create Strategy
            </button>
          </div>
        </div>

        {/* Symbol Search Section */}
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-xl font-semibold text-white mb-2">Symbol Search</h3>
          <p className="text-gray-400 text-sm mb-4">
            Search symbols to see both <span className="text-white font-semibold">universal format</span> (Best-Option) 
            and <span className="text-blue-400 font-semibold">broker-specific format</span> (AngelOne)
          </p>
          
          {/* Search Input */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3 mb-6">
            <div className="md:col-span-3">
              <input
                type="text"
                placeholder="Search symbols (e.g., NIFTY, BANKNIFTY, RELIANCE)..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-gray-700 text-white px-4 py-2 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
              />
            </div>
            <select
              value={selectedExchange}
              onChange={(e) => setSelectedExchange(e.target.value)}
              className="bg-gray-700 text-white px-4 py-2 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
            >
              <option value="">All Exchanges</option>
              <option value="NSE">NSE</option>
              <option value="NFO">NFO</option>
              <option value="BSE">BSE</option>
              <option value="BFO">BFO</option>
              <option value="MCX">MCX</option>
              <option value="CDS">CDS</option>
            </select>
          </div>

          {/* Search Results */}
          {searching && (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
              <p className="text-gray-400 mt-2">Searching...</p>
            </div>
          )}

          {!searching && searchResults.length > 0 && (
            <div className="overflow-x-auto">
              <div className="mb-3 text-sm text-gray-400">
                Found {searchResults.length} matching symbol{searchResults.length !== 1 ? 's' : ''}
              </div>
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-gray-700">
                    <th className="px-4 py-3 text-gray-300 font-semibold">Symbol (Universal)</th>
                    <th className="px-4 py-3 text-gray-300 font-semibold">BRSymbol (Broker)</th>
                    <th className="px-4 py-3 text-gray-300 font-semibold">Name</th>
                    <th className="px-4 py-3 text-gray-300 font-semibold">Exchange</th>
                    <th className="px-4 py-3 text-gray-300 font-semibold">Token</th>
                    <th className="px-4 py-3 text-gray-300 font-semibold">Expiry</th>
                    <th className="px-4 py-3 text-gray-300 font-semibold">Strike</th>
                    <th className="px-4 py-3 text-gray-300 font-semibold">Lot Size</th>
                  </tr>
                </thead>
                <tbody>
                  {searchResults.map((result, index) => (
                    <tr key={index} className="border-b border-gray-700 hover:bg-gray-700">
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <span className="text-white font-semibold">{result.symbol}</span>
                          <button
                            onClick={() => copyToClipboard(result.symbol, 'Symbol')}
                            className="text-gray-400 hover:text-white text-xs"
                            title="Copy symbol"
                          >
                            📋
                          </button>
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <span className="text-blue-400 font-semibold">{result.brsymbol}</span>
                          <button
                            onClick={() => copyToClipboard(result.brsymbol, 'BRSymbol')}
                            className="text-gray-400 hover:text-white text-xs"
                            title="Copy broker symbol"
                          >
                            📋
                          </button>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-gray-300 max-w-xs truncate">{result.name}</td>
                      <td className="px-4 py-3">
                        <span className="bg-blue-600 text-white px-2 py-1 rounded text-xs">
                          {result.exchange}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-gray-400 font-mono text-xs">{result.token}</td>
                      <td className="px-4 py-3 text-gray-400">{result.expiry || '-'}</td>
                      <td className="px-4 py-3 text-gray-400">{result.strike || '-'}</td>
                      <td className="px-4 py-3 text-gray-400">{result.lotsize || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {!searching && searchQuery.length >= 2 && searchResults.length === 0 && (
            <div className="text-center py-8">
              <p className="text-gray-400">No symbols found matching "{searchQuery}"</p>
              <p className="text-gray-500 text-sm mt-2">Try a different search term or exchange</p>
            </div>
          )}

          {!searching && searchQuery.length < 2 && (
            <div className="text-center py-8">
              <p className="text-gray-400">Enter at least 2 characters to search</p>
              <p className="text-gray-500 text-sm mt-2">
                Search by symbol (NIFTY), name (Reliance), or token number
              </p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default Dashboard;
