import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function Register() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirm_password: '',
    broker: '',
    broker_api_key: ''
  });
  const [brokers, setBrokers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Fetch available brokers
  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/auth/brokers')
      .then(res => res.json())
      .then(data => setBrokers(data.brokers || []))
      .catch(err => console.error('Failed to fetch brokers:', err));
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
      const response = await fetch('http://127.0.0.1:8000/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (response.ok) {
        // Save user to localStorage for login page
        const registeredUsers = JSON.parse(localStorage.getItem('registered_users') || '[]');
        registeredUsers.push({
          email: formData.email,
          broker: formData.broker,
          name: formData.name
        });
        localStorage.setItem('registered_users', JSON.stringify(registeredUsers));
        
        alert('Registration successful! Please login.');
        navigate('/login');
      } else {
        setError(data.detail || 'Registration failed');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const selectedBroker = brokers.find(b => b.id === formData.broker);

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
      <div className="bg-gray-800 rounded-lg shadow-xl p-8 w-full max-w-md">
        <h2 className="text-3xl font-bold text-white mb-6 text-center">
          Register - Best-Option
        </h2>

        {error && (
          <div className="bg-red-500 text-white p-3 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Name */}
          <div>
            <label className="block text-gray-300 mb-2">Full Name</label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              className="w-full px-4 py-2 bg-gray-700 text-white rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter your name"
            />
          </div>

          {/* Email */}
          <div>
            <label className="block text-gray-300 mb-2">Email</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              className="w-full px-4 py-2 bg-gray-700 text-white rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="your@email.com"
            />
          </div>

          {/* Password */}
          <div>
            <label className="block text-gray-300 mb-2">Password</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              minLength="8"
              className="w-full px-4 py-2 bg-gray-700 text-white rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Min 8 characters"
            />
          </div>

          {/* Confirm Password */}
          <div>
            <label className="block text-gray-300 mb-2">Confirm Password</label>
            <input
              type="password"
              name="confirm_password"
              value={formData.confirm_password}
              onChange={handleChange}
              required
              className="w-full px-4 py-2 bg-gray-700 text-white rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Re-enter password"
            />
          </div>

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

          {/* Broker API Key (conditional) */}
          {selectedBroker && selectedBroker.requires_api_key && (
            <div>
              <label className="block text-gray-300 mb-2">
                {selectedBroker.name} API Key
              </label>
              <input
                type="text"
                name="broker_api_key"
                value={formData.broker_api_key}
                onChange={handleChange}
                required
                className="w-full px-4 py-2 bg-gray-700 text-white rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter your broker API key"
              />
              <p className="text-gray-400 text-sm mt-1">
                Get this from your {selectedBroker.name} dashboard
              </p>
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded transition disabled:opacity-50"
          >
            {loading ? 'Registering...' : 'Register'}
          </button>
        </form>

        {/* Login Link */}
        <p className="text-gray-400 text-center mt-6">
          Already have an account?{' '}
          <button
            onClick={() => navigate('/login')}
            className="text-blue-400 hover:text-blue-300"
          >
            Login here
          </button>
        </p>
      </div>
    </div>
  );
}

export default Register;
