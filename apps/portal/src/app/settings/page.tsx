'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';

type SettingsTab = 'account' | 'appearance' | 'privacy' | 'notifications';

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<SettingsTab>('account');
  const [settings, setSettings] = useState({
    theme: 'dark-state' as const,
    notifications: true,
    soundEnabled: true,
    privacyLevel: 'public' as const,
  });

  const TABS: { id: SettingsTab; label: string; icon: string }[] = [
    { id: 'account', label: 'Account', icon: '👤' },
    { id: 'appearance', label: 'Appearance', icon: '🎨' },
    { id: 'privacy', label: 'Privacy', icon: '🛡️' },
    { id: 'notifications', label: 'Notifications', icon: '🔔' },
  ];

  return (
    <div className="min-h-screen w-full bg-black overflow-hidden">
      {/* Background Grid */}
      <div className="absolute inset-0 opacity-10">
        <div
          style={{
            backgroundImage: `linear-gradient(90deg, rgba(0, 243, 255, 0.05) 1px, transparent 1px),
                              linear-gradient(rgba(0, 243, 255, 0.05) 1px, transparent 1px)`,
            backgroundSize: '40px 40px',
          }}
        />
      </div>

      {/* Header */}
      <motion.nav
        className="relative z-40 flex items-center justify-between px-8 py-6 border-b border-white/5"
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
      >
        <Link href="/">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent cursor-pointer hover:scale-105 transition-transform">
            GEMIGRAM
          </h1>
        </Link>

        <Link href="/profile">
          <button className="text-sm text-white/70 hover:text-white transition-colors">
            Back to Profile
          </button>
        </Link>
      </motion.nav>

      {/* Main Content */}
      <div className="relative z-20 max-w-6xl mx-auto px-8 py-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-8"
        >
          <h2 className="text-4xl font-bold text-white mb-2">Settings</h2>
          <p className="text-white/60">Customize your Gemigram experience</p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Settings Tabs */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="lg:col-span-1"
          >
            <div className="rounded-2xl p-6 backdrop-blur-xl bg-black/40 border border-white/10 space-y-2 sticky top-8">
              {TABS.map((tab) => (
                <motion.button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className={`w-full text-left px-4 py-3 rounded-lg transition-all font-medium ${
                    activeTab === tab.id
                      ? 'bg-gradient-to-r from-cyan-500 to-purple-500 text-white'
                      : 'text-white/70 hover:text-white hover:bg-white/5'
                  }`}
                >
                  <span className="mr-2">{tab.icon}</span>
                  {tab.label}
                </motion.button>
              ))}
            </div>
          </motion.div>

          {/* Settings Content */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="lg:col-span-3"
          >
            <div className="rounded-2xl p-8 backdrop-blur-xl bg-black/40 border border-white/10">
              {/* Account Settings */}
              {activeTab === 'account' && (
                <div className="space-y-8">
                  <div>
                    <h3 className="text-2xl font-bold text-white mb-6">Account Settings</h3>

                    <div className="space-y-6">
                      {/* Email */}
                      <div>
                        <label className="block text-sm font-medium text-white/80 mb-2">
                          Email Address
                        </label>
                        <input
                          type="email"
                          defaultValue="user@gemigram.ai"
                          disabled
                          className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-white/60 focus:outline-none"
                        />
                      </div>

                      {/* Username */}
                      <div>
                        <label className="block text-sm font-medium text-white/80 mb-2">
                          Username
                        </label>
                        <input
                          type="text"
                          defaultValue="aether_user"
                          className="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-white focus:border-cyan-500 focus:outline-none transition-colors"
                        />
                      </div>

                      {/* Password */}
                      <div>
                        <label className="block text-sm font-medium text-white/80 mb-2">
                          Password
                        </label>
                        <motion.button
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          className="px-4 py-2 rounded-lg border border-white/20 text-white/70 hover:text-white hover:border-cyan-500 transition-colors text-sm font-medium"
                        >
                          Change Password
                        </motion.button>
                      </div>

                      {/* Danger Zone */}
                      <div className="pt-6 border-t border-white/10">
                        <h4 className="text-sm font-bold text-red-400 mb-4">Danger Zone</h4>
                        <motion.button
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          className="px-4 py-2 rounded-lg border border-red-500/50 text-red-400 hover:bg-red-500/10 transition-colors text-sm font-medium"
                        >
                          Delete Account
                        </motion.button>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Appearance Settings */}
              {activeTab === 'appearance' && (
                <div className="space-y-8">
                  <div>
                    <h3 className="text-2xl font-bold text-white mb-6">Appearance</h3>

                    <div className="space-y-6">
                      {/* Theme */}
                      <div>
                        <label className="block text-sm font-medium text-white/80 mb-4">
                          Theme
                        </label>
                        <div className="grid grid-cols-2 gap-3">
                          {['dark-state', 'white-hole'].map((theme) => (
                            <motion.button
                              key={theme}
                              onClick={() => setSettings({ ...settings, theme: theme as any })}
                              whileHover={{ scale: 1.02 }}
                              className={`p-4 rounded-lg border transition-all ${
                                settings.theme === theme
                                  ? 'bg-gradient-to-r from-cyan-500/20 to-purple-500/20 border-cyan-500/50'
                                  : 'bg-white/5 border-white/10 hover:border-white/20'
                              }`}
                            >
                              <p className="font-medium text-white capitalize">
                                {theme.replace('-', ' ')}
                              </p>
                              <p className="text-xs text-white/50 mt-1">
                                {theme === 'dark-state' ? 'Neural Dark' : 'Quantum Light'}
                              </p>
                            </motion.button>
                          ))}
                        </div>
                      </div>

                      {/* Accent Color */}
                      <div>
                        <label className="block text-sm font-medium text-white/80 mb-4">
                          Accent Color
                        </label>
                        <div className="flex gap-3">
                          {['cyan', 'purple', 'pink', 'emerald'].map((color) => (
                            <motion.button
                              key={color}
                              whileHover={{ scale: 1.1 }}
                              className={`w-12 h-12 rounded-lg border-2 transition-all ${
                                color === 'cyan'
                                  ? 'border-cyan-400'
                                  : color === 'purple'
                                  ? 'border-purple-400'
                                  : color === 'pink'
                                  ? 'border-pink-400'
                                  : 'border-emerald-400'
                              }`}
                              style={{
                                background:
                                  color === 'cyan'
                                    ? '#00F3FF'
                                    : color === 'purple'
                                    ? '#BC13FE'
                                    : color === 'pink'
                                    ? '#FF1CF7'
                                    : '#10B981',
                              }}
                            />
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Privacy Settings */}
              {activeTab === 'privacy' && (
                <div className="space-y-8">
                  <div>
                    <h3 className="text-2xl font-bold text-white mb-6">Privacy & Security</h3>

                    <div className="space-y-6">
                      {/* Privacy Level */}
                      <div>
                        <label className="block text-sm font-medium text-white/80 mb-4">
                          Profile Visibility
                        </label>
                        <div className="space-y-3">
                          {['public', 'private', 'friends'].map((level) => (
                            <label key={level} className="flex items-center gap-3 p-3 rounded-lg hover:bg-white/5 cursor-pointer transition-colors">
                              <input
                                type="radio"
                                name="privacy"
                                value={level}
                                checked={settings.privacyLevel === level}
                                onChange={(e) => setSettings({ ...settings, privacyLevel: e.target.value as any })}
                                className="w-4 h-4 accent-cyan-500"
                              />
                              <div>
                                <p className="font-medium text-white capitalize">{level}</p>
                                <p className="text-xs text-white/50">
                                  {level === 'public'
                                    ? 'Anyone can see your profile'
                                    : level === 'private'
                                    ? 'Only you can see your profile'
                                    : 'Only friends can see your profile'}
                                </p>
                              </div>
                            </label>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Notifications */}
              {activeTab === 'notifications' && (
                <div className="space-y-8">
                  <div>
                    <h3 className="text-2xl font-bold text-white mb-6">Notifications</h3>

                    <div className="space-y-4">
                      {[
                        { label: 'Agent Messages', desc: 'Receive notifications for agent messages' },
                        { label: 'Agent Activity', desc: 'Get alerts when agents are active' },
                        { label: 'Community Events', desc: 'Notifications about new community features' },
                      ].map((notification) => (
                        <label key={notification.label} className="flex items-center gap-4 p-4 rounded-lg hover:bg-white/5 cursor-pointer transition-colors">
                          <input type="checkbox" defaultChecked className="w-5 h-5 rounded accent-cyan-500" />
                          <div>
                            <p className="font-medium text-white">{notification.label}</p>
                            <p className="text-sm text-white/50">{notification.desc}</p>
                          </div>
                        </label>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Save Button */}
              <div className="mt-8 pt-8 border-t border-white/10 flex justify-end gap-4">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="px-6 py-2 rounded-lg border border-white/20 text-white/70 hover:text-white transition-colors"
                >
                  Cancel
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="px-6 py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-purple-500 text-white font-medium"
                >
                  Save Changes
                </motion.button>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
