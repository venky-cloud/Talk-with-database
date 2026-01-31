import { useState, useEffect } from 'react';
import { Home, LayoutDashboard, History, Terminal, MessageSquare, FileText, Settings, Database, Apple, Network, Code2} from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';

export default function Sidebar() {
  const [theme] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('theme') || 'dark';
    }
    return 'dark';
  });

  useEffect(() => {
    if (theme === 'light') {
      document.documentElement.classList.add('light');
      localStorage.setItem('theme', 'light');
    } else {
      document.documentElement.classList.remove('light');
      localStorage.setItem('theme', 'dark');
    }
  }, [theme]);
  const location = useLocation();
  
  const links = [
    { icon: Home, label: 'Home', path: '/' },
    { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard' },
    { 
      icon: Network, 
      label: 'Schema Workbench', 
      path: '/schema',
      color: 'text-cyan-400'
    },
    { 
      icon: Code2, 
      label: 'SQL Workbench', 
      path: '/sql-workbench',
      color: 'text-emerald-400'
    },
    { 
      icon: Terminal, 
      label: 'SQL Query', 
      path: '/sql-query',
      color: 'text-green-400'
    },
    { 
      icon: Database, 
      label: 'MongoDB Schema', 
      path: '/mongodb-schema',
      color: 'text-teal-400'
    },
    { 
      icon: Database, 
      label: 'MongoDB Workbench', 
      path: '/mongodb-workbench',
      color: 'text-green-500'
    },
    { 
      icon: Apple, 
      label: 'MongoDB Query', 
      path: '/mongodb-query',
      color: 'text-blue-400'
    },
    { 
      icon: Terminal, 
      label: 'API Query', 
      path: '/api-query',
      color: 'text-purple-400'
    },
    { icon: History, label: 'History', path: '/history' },
    { icon: MessageSquare, label: 'Chatbot', path: '/chatbot' },
    { icon: FileText, label: 'Documentation', path: '/docs' },
    { icon: Settings, label: 'Settings', path: '/settings' },
    { icon: Home, label: 'Login', path: '/login' }
  ];






  return (
    <aside className="w-64 h-screen fixed top-0 left-0 bg-black/70 backdrop-blur-md border-r border-[#00ff00]/30 flex flex-col glass-effect animate-fade-in transition-all duration-500">
      {/* Logo/Title */}
      <div className="flex items-center justify-between h-16 border-b border-[#00ff00]/30 px-4 animate-logo-pulse">
        <div className="flex items-center gap-3">
          <Database className="w-8 h-8 text-[#00ff00] animate-spin-slow" aria-label="App Logo" />
          <span className="text-[#00ff00] text-lg font-extrabold whitespace-nowrap tracking-wide">Talk with Database</span>
        </div>


      </div>
      {/* Navigation Links */}
      <nav className="flex-1 mt-4 px-2">
        <div className="space-y-1">
          {links.map(({ icon: Icon, label, path, color }) => (
            <Link
              key={path}
              to={path}
              aria-label={label}
              className={`sidebar-link transition-all duration-300 flex items-center px-3 py-2 text-base font-medium rounded-lg
                ${location.pathname === path
                  ? 'bg-[#00ff00]/10 text-[#00ff00] shadow-[0_0_10px_1px_#00ff00aa]'
                  : `text-gray-400 hover:${color || 'text-[#00ff00]'} hover:bg-[#00ff00]/5`}
              `}
            >
              <Icon className={`mr-3 h-5 w-5 transition-transform duration-300 group-hover:scale-110 ${color && location.pathname !== path ? color : ''}`} />
              {label}
            </Link>
          ))}
        </div>
      </nav>
    </aside>
  );
}



