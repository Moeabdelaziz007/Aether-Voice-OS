'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';

export default function ProfilePage() {
  const [isEditing, setIsEditing] = useState(false);
  const [profile, setProfile] = useState({
    username: 'aether_user',
    displayName: 'Aether Pioneer',
    email: 'user@gemigram.ai',
    bio: 'Exploring the neural nexus of AI communication',
    agentsCreated: 3,
    totalInteractions: 127,
    totalAuraPower: 245,
  });

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

        <div className="flex items-center gap-8">
          <Link href="/discover" className="text-sm text-white/70 hover:text-white transition-colors">
            Discover
          </Link>
          <Link href="/hub" className="text-sm text-white/70 hover:text-white transition-colors">
            Hub
          </Link>
          <Link href="/chat" className="text-sm text-white/70 hover:text-white transition-colors">
            Chat
          </Link>
          <span className="text-sm text-cyan-400 font-medium">Profile</span>
        </div>
      </motion.nav>

      {/* Main Content */}
      <div className="relative z-20 max-w-4xl mx-auto px-8 py-12">
        {/* Profile Header Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="rounded-2xl p-8 backdrop-blur-xl bg-gradient-to-br from-cyan-500/10 to-purple-500/10 border border-white/10 mb-8"
        >
          <div className="flex items-start justify-between mb-6">
            <div className="flex items-center gap-6">
              {/* Avatar */}
              <motion.div
                className="w-24 h-24 rounded-lg bg-gradient-to-br from-cyan-400 to-purple-500 flex items-center justify-center text-3xl font-bold"
                animate={{ boxShadow: ['0 0 20px rgba(0, 243, 255, 0.3)', '0 0 40px rgba(188, 19, 254, 0.4)', '0 0 20px rgba(0, 243, 255, 0.3)'] }}
                transition={{ duration: 3, repeat: Infinity }}
              >
                A
              </motion.div>

              {/* Info */}
              <div>
                <h1 className="text-3xl font-bold text-white mb-2">{profile.displayName}</h1>
                <p className="text-white/60 mb-3">@{profile.username}</p>
                <p className="text-sm text-white/70 max-w-md">{profile.bio}</p>
              </div>
            </div>

            {/* Edit Button */}
            <motion.button
              onClick={() => setIsEditing(!isEditing)}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="px-6 py-2 rounded-lg border border-white/20 text-white hover:border-cyan-500 hover:text-cyan-400 transition-colors text-sm font-medium"
            >
              {isEditing ? 'Done' : 'Edit Profile'}
            </motion.button>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-3 gap-4 pt-6 border-t border-white/10">
            <div>
              <p className="text-white/60 text-sm mb-2">Agents Created</p>
              <p className="text-2xl font-bold text-cyan-400">{profile.agentsCreated}</p>
            </div>
            <div>
              <p className="text-white/60 text-sm mb-2">Total Interactions</p>
              <p className="text-2xl font-bold text-purple-400">{profile.totalInteractions}</p>
            </div>
            <div>
              <p className="text-white/60 text-sm mb-2">Aura Power</p>
              <p className="text-2xl font-bold text-pink-400">{profile.totalAuraPower}</p>
            </div>
          </div>
        </motion.div>

        {/* Content Sections */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Column */}
          <div className="lg:col-span-2 space-y-8">
            {/* My Agents Section */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="rounded-2xl p-6 backdrop-blur-xl bg-black/40 border border-white/10"
            >
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-white">My Agents</h3>
                <Link href="/create">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="text-sm text-cyan-400 hover:text-cyan-300 transition-colors font-medium"
                  >
                    Create New
                  </motion.button>
                </Link>
              </div>

              <div className="space-y-3">
                {['Nova Prime', 'Atlas Protocol', 'Kora Genesis'].map((agentName, index) => (
                  <motion.div
                    key={agentName}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.4, delay: 0.2 + index * 0.1 }}
                    className="p-4 rounded-lg bg-white/5 border border-white/10 hover:border-cyan-500/50 transition-colors cursor-pointer group"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-medium text-white">{agentName}</h4>
                        <p className="text-xs text-white/50">Created 2 days ago</p>
                      </div>
                      <motion.div
                        className="w-2 h-2 rounded-full bg-emerald-400"
                        animate={{ scale: [1, 1.2, 1] }}
                        transition={{ duration: 2, repeat: Infinity }}
                      />
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>

            {/* Activity Section */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="rounded-2xl p-6 backdrop-blur-xl bg-black/40 border border-white/10"
            >
              <h3 className="text-xl font-bold text-white mb-6">Recent Activity</h3>

              <div className="space-y-4">
                {[
                  { action: 'Created agent "Nova Prime"', time: '2 hours ago' },
                  { action: 'Started conversation with Atlas', time: '5 hours ago' },
                  { action: 'Reached Aura Level 50', time: '1 day ago' },
                ].map((activity, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.4, delay: 0.3 + index * 0.1 }}
                    className="p-4 rounded-lg bg-white/5 border border-white/10"
                  >
                    <p className="text-white/80 text-sm">{activity.action}</p>
                    <p className="text-xs text-white/40 mt-1">{activity.time}</p>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Settings */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="rounded-2xl p-6 backdrop-blur-xl bg-black/40 border border-white/10"
            >
              <h3 className="text-lg font-bold text-white mb-4">Settings</h3>

              <div className="space-y-3">
                <Link href="/settings">
                  <button className="w-full text-left px-4 py-2 rounded-lg hover:bg-white/5 transition-colors text-white/70 hover:text-white text-sm">
                    ⚙️ Account Settings
                  </button>
                </Link>
                <button className="w-full text-left px-4 py-2 rounded-lg hover:bg-white/5 transition-colors text-white/70 hover:text-white text-sm">
                  🔔 Notifications
                </button>
                <button className="w-full text-left px-4 py-2 rounded-lg hover:bg-white/5 transition-colors text-white/70 hover:text-white text-sm">
                  🛡️ Privacy & Security
                </button>
                <button className="w-full text-left px-4 py-2 rounded-lg hover:bg-white/5 transition-colors text-red-400/70 hover:text-red-400 text-sm">
                  🚪 Sign Out
                </button>
              </div>
            </motion.div>

            {/* Achievements */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              className="rounded-2xl p-6 backdrop-blur-xl bg-black/40 border border-white/10"
            >
              <h3 className="text-lg font-bold text-white mb-4">Achievements</h3>

              <div className="space-y-2">
                {['🎯 First Agent', '🚀 10 Interactions', '⭐ Aura Master'].map((achievement) => (
                  <motion.div
                    key={achievement}
                    whileHover={{ scale: 1.02 }}
                    className="px-3 py-2 rounded-lg bg-gradient-to-r from-cyan-500/20 to-purple-500/20 border border-white/10 text-sm text-white/80"
                  >
                    {achievement}
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
}
