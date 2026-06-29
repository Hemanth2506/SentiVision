import React from 'react';
import { NavLink, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  MdDashboard, 
  MdPsychology, 
  MdCloudUpload, 
  MdHistory, 
  MdPerson, 
  MdLogout,
  MdMenuOpen,
  MdMenu
} from 'react-icons/md';

const Sidebar = ({ isOpen, toggleSidebar }) => {
  const { logout, user } = useAuth();

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: MdDashboard },
    { name: 'Text Analyzer', path: '/analyzer', icon: MdPsychology },
    { name: 'Bulk Analyzer', path: '/bulk', icon: MdCloudUpload },
    { name: 'Prediction History', path: '/history', icon: MdHistory },
  ];

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div 
          className="fixed inset-0 z-40 bg-slate-900/40 backdrop-blur-sm lg:hidden"
          onClick={toggleSidebar}
        />
      )}

      {/* Sidebar Container */}
      <aside className={`
        fixed top-0 bottom-0 left-0 z-50 flex flex-col w-64 border-r 
        bg-white border-slate-200 text-slate-800 transition-all duration-300 ease-in-out
        dark:bg-brand-navy dark:border-slate-800 dark:text-slate-100
        lg:translate-x-0 ${isOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        {/* Header Branding */}
        <div className="flex items-center justify-between h-20 px-6 border-b border-slate-200 dark:border-slate-800">
          <Link to="/dashboard" className="flex flex-col">
            <span className="text-xl font-bold tracking-tight text-brand-indigo dark:text-brand-indigoLight flex items-center gap-2">
              <span className="w-8 h-8 rounded-lg bg-gradient-to-tr from-brand-indigo to-violet-500 flex items-center justify-center text-white font-extrabold shadow-lg shadow-indigo-500/20 dark:shadow-none">S</span>
              SentiVision AI
            </span>
            <span className="text-[10px] text-slate-400 font-medium">Understand Every Word. Instantly.</span>
          </Link>
          <button 
            onClick={toggleSidebar}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 lg:hidden"
          >
            <MdMenuOpen size={24} />
          </button>
        </div>

        {/* User Info Card */}
        {user && (
          <div className="px-6 py-5 border-b border-slate-200 dark:border-slate-800 flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-indigo-500/10 text-brand-indigo dark:text-brand-indigoLight flex items-center justify-center font-bold text-lg border border-indigo-500/20">
              {user.name.charAt(0).toUpperCase()}
            </div>
            <div className="flex flex-col min-w-0">
              <span className="text-sm font-semibold truncate">{user.name}</span>
              <span className="text-xs text-slate-400 truncate">{user.email}</span>
            </div>
          </div>
        )}

        {/* Navigation Items */}
        <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
          {navItems.map((item) => (
            <NavLink
              key={item.name}
              to={item.path}
              onClick={() => {
                // Close sidebar on mobile select
                if (window.innerWidth < 1024) toggleSidebar();
              }}
              className={({ isActive }) => `
                flex items-center gap-3 px-4 py-3 text-sm font-medium rounded-xl transition-all duration-200
                ${isActive 
                  ? 'bg-brand-indigo/10 text-brand-indigo dark:bg-brand-indigo/20 dark:text-brand-indigoLight shadow-sm shadow-brand-indigo/5' 
                  : 'text-slate-500 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800/60 dark:hover:text-slate-100'}
              `}
            >
              <item.icon size={20} className="flex-shrink-0" />
              {item.name}
            </NavLink>
          ))}
        </nav>

        {/* Logout Section */}
        <div className="p-4 border-t border-slate-200 dark:border-slate-800">
          <button
            onClick={logout}
            className="flex items-center gap-3 w-full px-4 py-3 text-sm font-medium text-rose-500 rounded-xl hover:bg-rose-500/10 transition-colors"
          >
            <MdLogout size={20} />
            Sign Out
          </button>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
