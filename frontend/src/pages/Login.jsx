import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function Login() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    broker: '',
    client_id: '',
    pin: '',
    totp: ''
  });
  const [brokers, setBrokers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Fetch available brokers
  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/auth/brokers')
      .then(res => res.json())
      .then(data => {
        console.log('Brokers fetched:', data);
        setBrokers(data.brokers || []);
      })
      .catch(err => {
        console.error('Failed to fetch brokers:', err);
        // Set default broker if API fails
        setBrokers([
          { id: 'angelone', name: 'AngelOne', status: 'active', requires_api_key: true }
        ]);
      });
  }, []);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Fyers uses OAuth flow - redirect to Fyers login page
      if (formData.broker === 'fyers') {
        // Get user's Fyers credentials from database
        // First, we need to get the user by broker
        const userResponse = await fetch(`http://127.0.0.1:8000/api/auth/user-by-broker?broker=fyers`);
        
        if (!userResponse.ok) {
          setError('No Fyers account found. Please register first.');
          setLoading(false);
          return;
        }
        
        const userData = await userResponse.json();
        const apiKey = userData.broker_api_key;  // App ID
        const redirectUri = userData.redirect_url || `${window.location.origin}/fyers-callback`;
        
        if (!apiKey) {
          setError('Fyers App ID not found. Please register again.');
          setLoading(false);
          return;
        }
        
        // Store user info for callback page
        localStorage.setItem('fyers_user', JSON.stringify(userData));
        
        // Redirect to Fyers authorization page
        // Using v3 API (same as OpenAlgo) with production environment (api-t1)
        const fyersAuthUrl = `https://api-t1.fyers.in/api/v3/generate-authcode?client_id=${apiKey}&redirect_uri=${encodeURIComponent(redirectUri)}&response_type=code&state=sample_state`;
        
        console.log('Redirecting to Fyers:', fyersAuthUrl);
        window.location.href = fyersAuthUrl;
        return;
      }
      
      // AngelOne uses direct authentication
      const response = await fetch('http://127.0.0.1:8000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)  // Send only broker credentials, no email
      });

      const data = await response.json();

      if (response.ok) {
        // Store user data and tokens
        localStorage.setItem('user', JSON.stringify(data.user));
        localStorage.setItem('auth_token', data.auth_token);
        localStorage.setItem('feed_token', data.feed_token);
        
        alert('Login successful!');
        navigate('/dashboard');
      } else {
        setError(data.detail || 'Login failed');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
      <div className="bg-gray-800 rounded-lg shadow-xl p-8 w-full max-w-md">
        <h2 className="text-3xl font-bold text-white mb-6 text-center">
          Login - Best-Option
        </h2>

        {error && (
          <div className="bg-red-500 text-white p-3 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Broker Selection */}
          <div>
            <label className="block text-gray-300 mb-2">Select Broker</label>
            <select
              name="broker"
              value={formData.broker}
              onChange={handleChange}
              required
              className="w-full px-4 py-2 bg-gray-700 text-white rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">-- Select Broker --</option>
              {brokers.map(broker => (
                <option 
                  key={broker.id} 
                  value={broker.id}
                  disabled={broker.status !== 'active'}
                >
                  {broker.name} {broker.status !== 'active' && '(Coming Soon)'}
                </option>
              ))}
            </select>
          </div>

          {/* Broker Credentials (show when broker selected) */}
          {formData.broker === 'angelone' && (
            <>
              {/* Client ID */}
              <div>
                <label className="block text-gray-300 mb-2">Client ID</label>
                <input
                  type="text"
                  name="client_id"
                  value={formData.client_id}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-2 bg-gray-700 text-white rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter your client ID"
                />
              </div>

              {/* PIN */}
              <div>
                <label className="block text-gray-300 mb-2">PIN</label>
                <input
                  type="password"
                  name="pin"
                  value={formData.pin}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-2 bg-gray-700 text-white rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter your PIN"
                />
              </div>

              {/* TOTP */}
              <div>
                <label className="block text-gray-300 mb-2">TOTP (6 digits)</label>
                <input
                  type="text"
                  name="totp"
                  value={formData.totp}
                  onChange={handleChange}
                  required
                  maxLength="6"
                  pattern="[0-9]{6}"
                  className="w-full px-4 py-2 bg-gray-700 text-white rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter 6-digit TOTP"
                />
                <p className="text-gray-400 text-sm mt-1">
                  Get this from your authenticator app
                </p>
              </div>
            </>
          )}
          
          {/* Fyers OAuth Login */}
          {formData.broker === 'fyers' && (
            <div className="bg-blue-900 p-4 rounded">
              <p className="text-gray-300 text-sm mb-2">
                Fyers uses OAuth authentication. Click Login to be redirected to Fyers login page.
              </p>
              <p className="text-gray-400 text-xs">
                You'll need your Fyers API Key and Secret (from registration).
              </p>
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded transition disabled:opacity-50"
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        {/* Register Link */}
        <p className="text-gray-400 text-center mt-6">
          Don't have an account?{' '}
          <button
            onClick={() => navigate('/register')}
            className="text-blue-400 hover:text-blue-300"
          >
            Register here
          </button>
        </p>
      </div>
    </div>
  );
}

export default Login;
