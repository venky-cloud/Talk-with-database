import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import History from './pages/History';
import Chatbot from './pages/Chatbot';
import Documentation from './pages/Documentation';
import Settings from './pages/Settings';
import SqlQuery from './pages/SqlQuery';
import ApiQuery from './pages/ApiQuery';
import MongoDbQuery from './pages/MongoDbQuery';
import SchemaWorkbench from './pages/SchemaWorkbench';
import SqlWorkbench from './pages/SqlWorkbench';
import MongoDBWorkbench from './pages/MongoDBWorkbench';
import MongoDBSchemaWorkbench from './pages/MongoDBSchemaWorkbench';
import Login from './pages/Login';
import ProtectedRoute from './components/ProtectedRoute';
import { AuthProvider } from './contexts/AuthContext';
import { ToastProvider } from './contexts/ToastContext';
import { Navigate } from 'react-router-dom';
import { ThemeEffectsProvider, useThemeEffects } from './contexts/ThemeEffectsContext';

function AppContent() {
  const location = useLocation();
  const isLogin = location.pathname === '/login';
  const { shouldSnow, isMobile, densityMobile, densityDesktop } = useThemeEffects();
  return (
    <div className="min-h-screen bg-black text-white relative">
      {/* Global animated background (disabled on /login to avoid duplication) */}
      {!isLogin && (
        <>
          <div className="login-grid"></div>
          <div className="login-blob w-80 h-80 bg-emerald-600/30 top-[-60px] left-[-60px] animate-float-slow absolute"></div>
          <div className="login-blob w-80 h-80 bg-blue-600/30 bottom-[-60px] right-[-60px] animate-float-slow absolute" style={{ animationDelay: '1.2s' }}></div>
        </>
      )}
      {shouldSnow && (
        <div className="snowflakes" aria-hidden>
          {Array.from({ length: isLogin ? 1 : (isMobile ? densityMobile : densityDesktop) }).map((_, i) => (
            <span
              key={i}
              style={{
                left: `${(i * 83) % 100}%`,
                animationDuration: `${7 + (i % 6)}s`,
                animationDelay: `${(i % 10) / 7}s`,
              }}
            >
              ❄
            </span>
          ))}
        </div>
      )}
      {!isLogin && <Navbar />}
      <div className="flex relative z-10">
        {!isLogin && <Sidebar />}
        <main className={`flex-1 transition-all duration-300 ${!isLogin ? 'pl-64' : ''}`}>
          <Routes>
              <Route path="/" element={<Navigate to="/login" replace />} />
              <Route path="/login" element={<Login />} />
              <Route path="/home" element={<ProtectedRoute><Home /></ProtectedRoute>} />
              <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
              <Route path="/history" element={<ProtectedRoute><History /></ProtectedRoute>} />
              <Route path="/chatbot" element={<ProtectedRoute><Chatbot /></ProtectedRoute>} />
              <Route path="/docs" element={<ProtectedRoute><Documentation /></ProtectedRoute>} />
              <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
              <Route path="/sql-query" element={<ProtectedRoute><SqlQuery /></ProtectedRoute>} />
              <Route path="/api-query" element={<ProtectedRoute><ApiQuery /></ProtectedRoute>} />
              <Route path="/mongodb-query" element={<ProtectedRoute><MongoDbQuery /></ProtectedRoute>} />
              <Route path="/schema" element={<ProtectedRoute><SchemaWorkbench /></ProtectedRoute>} />
              <Route path="/sql-workbench" element={<ProtectedRoute><SqlWorkbench /></ProtectedRoute>} />
              <Route path="/mongodb-workbench" element={<ProtectedRoute><MongoDBWorkbench /></ProtectedRoute>} />
              <Route path="/mongodb-schema" element={<ProtectedRoute><MongoDBSchemaWorkbench /></ProtectedRoute>} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <ToastProvider>
          <ThemeEffectsProvider>
            <AppContent />
          </ThemeEffectsProvider>
        </ToastProvider>
      </AuthProvider>
    </Router>
  );
}

export default App;