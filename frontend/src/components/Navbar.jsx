import React, { useState, useEffect } from 'react';
import { MdMenu, MdLightMode, MdDarkMode, MdPerson, MdNotifications } from 'react-icons/md';
import { useAuth } from '../context/AuthContext';

const Navbar = ({ toggleSidebar }) => {
  const { user } = useAuth();
  const [darkMode, setDarkMode] = useState(() => {
    // Check local storage or system preferences on initial load
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      return savedTheme === 'dark';
    }
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  // Apply dark class to body and documentElement elements when state changes
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
      document.body.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      document.body.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  }, [darkMode]);

  return (
    <header className="sticky top-0 z-30 flex items-center justify-between h-20 px-6 border-b bg-white/80 border-slate-200 backdrop-blur-md dark:bg-brand-navy/80 dark:border-slate-800 transition-colors">
      {/* Left Menu Toggle */}
      <div className="flex items-center gap-4">
        <button
          onClick={toggleSidebar}
          className="p-2 -ml-2 rounded-xl text-slate-500 hover:bg-slate-100 hover:text-slate-700 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-slate-200 lg:hidden"
        >
          <MdMenu size={24} />
        </button>
        <h1 className="text-lg font-semibold tracking-tight text-slate-700 dark:text-slate-300 hidden md:block">
          Welcome back, <span className="text-slate-900 dark:text-white font-bold">{user?.name || 'Guest'}</span>
        </h1>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-2">
        {/* Dark Mode Toggle */}
        <button
          onClick={() => setDarkMode(!darkMode)}
          className="p-2.5 rounded-xl border border-slate-200 bg-white text-slate-500 hover:bg-slate-50 dark:bg-slate-800 dark:border-slate-700 dark:text-slate-400 dark:hover:bg-slate-700/60 transition-colors shadow-sm"
          title="Toggle Dark/Light Mode"
        >
          {darkMode ? <MdLightMode size={20} className="text-amber-500" /> : <MdDarkMode size={20} />}
        </button>

        {/* Separator */}
        <div className="h-6 w-px bg-slate-200 dark:bg-slate-700 mx-2" />

        {/* User Badge */}
        <div className="flex items-center gap-3 pl-1">
          <div className="text-right hidden sm:block">
            <p className="text-xs font-semibold text-slate-800 dark:text-slate-200 leading-none">{user?.name}</p>
            <p className="text-[10px] text-slate-400 mt-1">Free Tier User</p>
          </div>
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-indigo to-violet-500 flex items-center justify-center text-white font-bold border border-slate-200 dark:border-slate-700 shadow-sm shadow-indigo-500/10">
            {user?.name?.substring(0, 2).toUpperCase() || 'US'}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
