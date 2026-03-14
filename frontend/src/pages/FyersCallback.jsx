import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

function FyersCallback() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState('Processing...');
  const [error, setError] = useState('');

  useEffect(() => {
    const handleCallback = async () => {
      // Get authorization code from URL
      const authCode = searchParams.get('auth_code');
      const state = searchParams.get('state');
      
      console.log('Fyers Callback - Auth Code:', authCode);
      console.log('Fyers Callback - State:', state);
      
      if (!authCode) {
        console.error('No auth_code in URL');
        setError('No authorization code received from Fyers');
        return;
      }

      try {
        setStatus('Authenticating with Fyers...');
        console.log('Sending request to backend...');
        
        // Send request_token to backend (no email needed - backend will find user by broker)
        const response = await fetch('http://127.0.0.1:8000/api/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            broker: 'fyers',
            request_token: authCode
          })
        });

        console.log('Backend response status:', response.status);
        const data = await response.json();
        console.log('Backend response data:', data);

        if (response.ok) {
          // Store user data and tokens
          localStorage.setItem('user', JSON.stringify(data.user));
          localStorage.setItem('auth_token', data.auth_token);
          localStorage.setItem('feed_token', data.feed_token);
          
          // Clear temporary storage
          localStorage.removeItem('fyers_user');
          
          console.log('Login successful! Redirecting to dashboard...');
          setStatus('Login successful! Redirecting...');
          setTimeout(() => {
            navigate('/dashboard');
          }, 1000);
        } else {
          console.error('Backend error:', data.detail);
          setError(data.detail || 'Authentication failed');
        }
      } catch (err) {
        console.error('Callback error:', err);
        setError(`Network error: ${err.message}. Is backend running on http://127.0.0.1:8000?`);
      }
    };

    handleCallback();
  }, [searchParams, navigate]);

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
      <div className="bg-gray-800 rounded-lg shadow-xl p-8 w-full max-w-md text-center">
        <h2 className="text-2xl font-bold text-white mb-4">
          Fyers Authentication
        </h2>
        
        {error ? (
          <div className="bg-red-500 text-white p-4 rounded mb-4">
            {error}
          </div>
        ) : (
          <div className="text-gray-300">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <p>{status}</p>
          </div>
        )}
        
        {error && (
          <button
            onClick={() => navigate('/login')}
            className="mt-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded"
          >
            Back to Login
          </button>
        )}
      </div>
    </div>
  );
}

export default FyersCallback;
