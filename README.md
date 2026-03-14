# Best-Option Desktop Application

A desktop trading application for options analysis and trading with broker integration.

## Features

- **Multi-Broker Support**: Currently supports AngelOne broker
- **Symbol Search**: Search and compare universal vs broker-specific symbol formats
- **Master Contract Management**: Automatic download and caching of 200K+ symbols
- **Authentication System**: Secure user registration and login
- **Real-time Data**: Master contract status monitoring
- **Desktop Application**: Built with Electron for cross-platform support

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: Database ORM
- **SQLite**: Lightweight database
- **Argon2**: Password hashing

### Frontend
- **React**: UI library
- **Vite**: Build tool
- **React Router**: Navigation
- **Tailwind CSS**: Styling
- **Electron**: Desktop wrapper

## Project Structure

```
best-option/
├── broker/              # Broker integrations
│   └── angelone/       # AngelOne broker plugin
├── database/           # Database models and operations
├── routes/             # API endpoints
├── services/           # Business logic
├── strategies/         # Trading strategies
├── websocket_proxy/    # WebSocket proxy server
├── frontend/           # React frontend
│   └── src/
│       ├── pages/      # React pages
│       └── App.jsx     # Main app component
├── docs/               # Documentation
├── app.py              # FastAPI application
└── requirements.txt    # Python dependencies
```

## Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. Clone the repository:
```bash
git clone https://github.com/RahulEdward/starterkit.git
cd starterkit
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

5. Run backend:
```bash
python app.py
```

Backend will run on `http://127.0.0.1:8000`

### Frontend Setup

1. Navigate to frontend:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run development server:
```bash
npm run dev
```

Frontend will run on `http://localhost:5173`

## Usage

### Registration
1. Open the application
2. Click "Register" 
3. Enter your details:
   - Name
   - Email
   - Password
   - Select Broker (AngelOne)
   - Enter Broker API Key

### Login
1. Select your broker
2. Enter Client ID
3. Enter PIN
4. Enter TOTP (if enabled)

### Symbol Search
1. Navigate to Dashboard
2. Use the Symbol Search section
3. Type at least 2 characters
4. View results showing:
   - **Symbol (Universal)**: Best-Option format
   - **BRSymbol (Broker)**: AngelOne format
5. Filter by exchange (NSE, NFO, BSE, etc.)
6. Copy symbols to clipboard

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user

### Master Contract
- `GET /api/master-contract/status` - Get download status

### Search
- `GET /api/search/symbols` - Search symbols

## Database Schema

### Users Table
- id, name, email, password_hash, broker, created_at

### Broker Auth Table
- id, user_id, broker, broker_user_id, auth_token, feed_token, is_active

### Master Contract Status Table
- broker, status, message, last_updated, total_symbols, is_ready

## Symbol Management

The application uses an in-memory cache for fast symbol lookups:
- 200K+ symbols loaded at startup
- O(1) lookup performance
- Supports fuzzy search
- Exchange filtering

## Security

- Passwords hashed with Argon2 + pepper
- JWT tokens for broker authentication
- Secure session management
- Environment-based configuration

## Development

### Running Tests
```bash
# Backend tests
pytest

# Frontend tests
cd frontend
npm test
```

### Building for Production

#### Backend
```bash
# Backend runs as-is with Python
python app.py
```

#### Frontend
```bash
cd frontend
npm run build
```

#### Electron Desktop App
```bash
cd frontend
npm run electron:build
```

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

This project is licensed under the MIT License.

## Acknowledgments

- Inspired by OpenAlgo architecture
- AngelOne broker integration
- FastAPI framework
- React ecosystem

## Support

For issues and questions:
- GitHub Issues: https://github.com/RahulEdward/starterkit/issues
- Email: support@best-option.com

## Roadmap

- [ ] Add more broker integrations
- [ ] Options chain visualization
- [ ] 3D open interest maps
- [ ] Strategy backtesting
- [ ] Real-time WebSocket feeds
- [ ] Mobile application
- [ ] Advanced charting
- [ ] Paper trading mode

---

Built with ❤️ for traders
