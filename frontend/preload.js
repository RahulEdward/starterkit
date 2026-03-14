/**
 * Electron Preload Script
 * Secure bridge between main process and renderer
 */
const { contextBridge } = require('electron');

contextBridge.exposeInMainWorld('electron', {
  platform: process.platform,
  version: process.versions.electron
});
