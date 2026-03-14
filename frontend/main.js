/**
 * Electron Main Process
 * Launches the desktop application and manages the window
 */
const { app, BrowserWindow } = require('electron');
const path = require('path');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
    title: 'Best-Option - Options Trading Analytics',
  });

  // Always load from file in packaged app
  const indexPath = path.join(__dirname, 'dist', 'index.html');
  console.log('Loading from:', indexPath);
  mainWindow.loadFile(indexPath);
  
  // Open DevTools for debugging
  mainWindow.webContents.openDevTools();

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.on('ready', () => {
  console.log('Starting Best-Option Desktop App');
  console.log('Backend should be running on http://127.0.0.1:8000');
  console.log('If not running, please start: python app.py');
  createWindow();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});
