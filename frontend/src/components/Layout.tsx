// frontend/src/components/Layout.tsx
/* eslint-disable @typescript-eslint/no-explicit-any */
import { useCallback } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, Camera, Activity, Hand} from 'lucide-react';
import SystemStatus from './SystemStatus';

const TopBar = () => {
  const location = useLocation();

  const menuItems = [
    { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/live', icon: Camera, label: 'Live View' },
    { path: '/training', icon: Hand, label: 'Training' },
    { path: '/analytics', icon: Activity, label: 'Logs' },
  ];

  const handleStatusChange = useCallback((status: string) => {
    console.log('System status:', status);
  }, []);

  return (
    <header className="bg-industrial-gray border-b border-gray-700 h-16 flex items-center justify-between px-6 sticky top-0 z-50 shadow-md shadow-black/20">
      {/* Lewa: Logo */}
      <div className="flex items-center gap-3">
        <div className="bg-gradient-to-br from-accent-blue to-blue-600 p-2 rounded-lg shadow-lg shadow-blue-900/20">
          <Hand className="text-white" size={20} />
        </div>
        <h1 className="text-xl font-bold text-white tracking-tight">GestureAI</h1>
      </div>

      {/* Środek: Menu */}
      <nav className="flex items-center gap-1 bg-black/20 p-1 rounded-xl border border-white/5 hidden lg:flex">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                isActive 
                  ? 'bg-accent-blue text-white shadow-md' 
                  : 'text-gray-400 hover:text-white hover:bg-white/5'
              }`}
            >
              <Icon size={16} />
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Prawa: System Status */}
      <div className="flex items-center gap-3 pl-6 border-l border-gray-700">
        <span className="text-xs text-gray-500 font-bold tracking-wider uppercase hidden xl:block">SYSTEM STATUS</span>
        <SystemStatus onStatusChange={handleStatusChange} />
      </div>
    </header>
  );
};

const Layout = ({ children }: any) => {
  return (
    <div className="min-h-screen bg-industrial-dark text-white font-sans selection:bg-accent-blue selection:text-white flex flex-col">
      <TopBar />
      <main className="flex-1 p-6 w-full max-w-[1920px] mx-auto">
        {children}
      </main>
    </div>
  );
};

export default Layout;