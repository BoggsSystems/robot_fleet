import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import App from './App';

console.log('🔍 Index: Starting React app initialization...');

const rootElement = document.getElementById('root');
console.log('🔍 Index: Root element found:', !!rootElement);

if (!rootElement) {
  console.error('❌ Index: Root element not found!');
} else {
  const root = ReactDOM.createRoot(rootElement);
  console.log('🔍 Index: React root created successfully');

  try {
    root.render(
      <React.StrictMode>
        <BrowserRouter>
          <AuthProvider>
            <App />
          </AuthProvider>
        </BrowserRouter>
      </React.StrictMode>
    );
    console.log('✅ Index: React app rendered successfully');
  } catch (error) {
    console.error('❌ Index: Error rendering React app:', error);
    rootElement.innerHTML = `
      <div style="padding: 20px; color: white; font-family: monospace;">
        <h2>React App Error</h2>
        <p>Check browser console for details</p>
        <pre>${error}</pre>
      </div>
    `;
  }
}
