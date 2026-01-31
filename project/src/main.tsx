import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

// Debug environment variables
console.log('Environment Variables:', import.meta.env)
console.log('VITE_API_BASE:', import.meta.env.VITE_API_BASE);

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
