import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { toast } from 'react-hot-toast';
import { MdEmail, MdLock, MdArrowForward } from 'react-icons/md';

const Login = () => {
  const { login, forgotPassword } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isForgotPasswordOpen, setIsForgotPasswordOpen] = useState(false);
  const [forgotEmail, setForgotEmail] = useState('');
  const [isForgotSubmitting, setIsForgotSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      toast.error('Please fill in all fields.');
      return;
    }

    setIsSubmitting(true);
    try {
      await login(email, password);
      toast.success('Successfully logged in!');
      navigate('/dashboard');
    } catch (err) {
      toast.error(err || 'Invalid email or password.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleForgotPassword = async (e) => {
    e.preventDefault();
    if (!forgotEmail) {
      toast.error('Please enter your email.');
      return;
    }

    setIsForgotSubmitting(true);
    try {
      const data = await forgotPassword(forgotEmail);
      // Display the mock reset token in a success toast or alert
      toast.success(data.message, { duration: 6000 });
      if (data.reset_token) {
        // Display details in UI for demo purposes
        alert(`Demo Mode Reset Info:\n\nNormally an email is sent. For local preview, your password reset token is:\n\n${data.reset_token}\n\nUse this to reset your account.`);
      }
      setIsForgotPasswordOpen(false);
      setForgotEmail('');
    } catch (err) {
      toast.error(err || 'Failed to request password reset.');
    } finally {
      setIsForgotSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-950 text-white font-sans px-6 relative overflow-hidden">
      {/* Background Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

      {/* Main Login Card */}
      <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl relative z-10">
        
        {/* Logo/Title */}
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-500 to-purple-600 items-center justify-center font-extrabold text-white text-xl shadow-lg shadow-indigo-500/20 mb-4">S</Link>
          <h2 className="text-2xl font-bold tracking-tight">Welcome to SentiVision AI</h2>
          <p className="text-xs text-slate-400 mt-2">Sign in to your platform console</p>
        </div>

        {/* Normal login form */}
        {!isForgotPasswordOpen ? (
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Email Field */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300">Email Address</label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-500">
                  <MdEmail size={18} />
                </span>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 bg-slate-950 border border-slate-800 rounded-xl focus:border-indigo-500 focus:outline-none text-sm placeholder-slate-600 transition-colors"
                  placeholder="name@company.com"
                  required
                />
              </div>
            </div>

            {/* Password Field */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label className="text-xs font-semibold text-slate-300">Password</label>
                <button
                  type="button"
                  onClick={() => setIsForgotPasswordOpen(true)}
                  className="text-xs text-indigo-400 hover:text-indigo-300 font-semibold"
                >
                  Forgot Password?
                </button>
              </div>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-500">
                  <MdLock size={18} />
                </span>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 bg-slate-950 border border-slate-800 rounded-xl focus:border-indigo-500 focus:outline-none text-sm placeholder-slate-600 transition-colors"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full py-3.5 bg-gradient-to-tr from-indigo-600 to-purple-600 rounded-xl font-bold hover:from-indigo-500 hover:to-purple-500 flex items-center justify-center gap-2 group shadow-lg shadow-indigo-500/20 active:scale-98 transition-all disabled:opacity-50"
            >
              {isSubmitting ? 'Verifying identity...' : 'Sign In'}
              <MdArrowForward size={18} className="group-hover:translate-x-1 transition-transform" />
            </button>
          </form>
        ) : (
          /* Forgot Password Mock Form */
          <form onSubmit={handleForgotPassword} className="space-y-5">
            <p className="text-xs text-slate-400 leading-relaxed mb-4">
              Enter your registered email address and we'll generate a secure reset token for your account.
            </p>
            
            {/* Email Field */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300">Email Address</label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-500">
                  <MdEmail size={18} />
                </span>
                <input
                  type="email"
                  value={forgotEmail}
                  onChange={(e) => setForgotEmail(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 bg-slate-950 border border-slate-800 rounded-xl focus:border-indigo-500 focus:outline-none text-sm placeholder-slate-600 transition-colors"
                  placeholder="name@company.com"
                  required
                />
              </div>
            </div>

            <div className="flex items-center gap-4">
              <button
                type="button"
                onClick={() => setIsForgotPasswordOpen(false)}
                className="w-1/2 py-3 border border-slate-800 hover:bg-slate-800 rounded-xl text-sm font-semibold transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isForgotSubmitting}
                className="w-1/2 py-3 bg-white text-slate-950 hover:bg-slate-100 rounded-xl text-sm font-bold transition-all disabled:opacity-50"
              >
                {isForgotSubmitting ? 'Requesting...' : 'Get Token'}
              </button>
            </div>
          </form>
        )}

        {/* Footer */}
        <div className="mt-8 pt-6 border-t border-slate-800 text-center text-xs text-slate-500">
          New to SentiVision?{' '}
          <Link to="/signup" className="text-indigo-400 hover:text-indigo-300 font-bold transition-colors">
            Create Account
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Login;
