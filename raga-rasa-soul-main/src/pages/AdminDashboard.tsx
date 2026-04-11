import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api';

interface DashboardStats {
  total_users: number;
  admin_count: number;
  total_songs: number;
  total_sessions: number;
  completed_sessions: number;
  avg_rating: number;
}

interface User {
  user_id: string;
  email: string;
  role: string;
  created_at: string;
}

interface Song {
  _id: string;
  title: string;
  artist: string;
  rasa: string;
}

const AdminDashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [songs, setSongs] = useState<Song[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState<'overview' | 'users' | 'songs'>('overview');
  const [promoteUserId, setPromoteUserId] = useState('');
  const [demoteUserId, setDemoteUserId] = useState('');
  const [deleteSongId, setDeleteSongId] = useState('');

  // Fetch dashboard stats
  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/admin/dashboard`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('auth_token')}` },
      });
      setStats(response.data);
    } catch (err: any) {
      setError('Failed to fetch dashboard statistics');
      console.error(err);
    }
  };

  // Fetch users list
  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/admin/users`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('auth_token')}` },
      });
      setUsers(response.data.users);
    } catch (err: any) {
      setError('Failed to fetch users');
      console.error(err);
    }
  };

  // Fetch songs list
  const fetchSongs = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/admin/songs`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('auth_token')}` },
      });
      setSongs(response.data.songs);
    } catch (err: any) {
      setError('Failed to fetch songs');
      console.error(err);
    }
  };

  // Promote user
  const handlePromoteUser = async (userId: string) => {
    try {
      await axios.post(
        `${API_BASE_URL}/admin/promote?user_id=${userId}`,
        {},
        {
          headers: { Authorization: `Bearer ${localStorage.getItem('auth_token')}` },
        }
      );
      setPromoteUserId('');
      await fetchUsers();
    } catch (err: any) {
      setError('Failed to promote user');
      console.error(err);
    }
  };

  // Demote admin
  const handleDemoteAdmin = async (userId: string) => {
    try {
      await axios.post(
        `${API_BASE_URL}/admin/demote?user_id=${userId}`,
        {},
        {
          headers: { Authorization: `Bearer ${localStorage.getItem('auth_token')}` },
        }
      );
      setDemoteUserId('');
      await fetchUsers();
    } catch (err: any) {
      setError('Failed to demote admin');
      console.error(err);
    }
  };

  // Delete song
  const handleDeleteSong = async (songId: string) => {
    try {
      await axios.delete(`${API_BASE_URL}/admin/song/${songId}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('auth_token')}` },
      });
      setDeleteSongId('');
      await fetchSongs();
    } catch (err: any) {
      setError('Failed to delete song');
      console.error(err);
    }
  };

  // Initial load
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchStats(), fetchUsers(), fetchSongs()]);
      setLoading(false);
    };
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-purple-800 to-indigo-900 flex items-center justify-center">
        <div className="text-white text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-400 mx-auto mb-4"></div>
          <p>Loading admin dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-purple-800 to-indigo-900 p-8">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">Admin Dashboard</h1>
            <p className="text-purple-200">Welcome, {user?.email}</p>
          </div>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={logout}
            className="px-6 py-3 bg-red-500 hover:bg-red-600 text-white rounded-lg transition"
          >
            Logout
          </motion.button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="max-w-7xl mx-auto mb-6 p-4 bg-red-500 bg-opacity-20 border border-red-400 rounded-lg"
        >
          <p className="text-red-200">{error}</p>
        </motion.div>
      )}

      {/* Tab Navigation */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="flex space-x-4 border-b border-purple-400 border-opacity-20">
          {(['overview', 'users', 'songs'] as const).map((tab) => (
            <motion.button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-6 py-3 font-semibold transition ${
                activeTab === tab
                  ? 'text-purple-300 border-b-2 border-purple-400'
                  : 'text-purple-200 hover:text-purple-100'
              }`}
              whileHover={{ scale: 1.05 }}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </motion.button>
          ))}
        </div>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && stats && (
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Total Users */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white bg-opacity-10 backdrop-blur-lg rounded-xl p-6 border border-white border-opacity-20"
            >
              <h3 className="text-purple-200 text-sm font-semibold mb-2">Total Users</h3>
              <p className="text-4xl font-bold text-white">{stats.total_users}</p>
              <p className="text-purple-300 text-xs mt-2">{stats.admin_count} admins</p>
            </motion.div>

            {/* Total Songs */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-white bg-opacity-10 backdrop-blur-lg rounded-xl p-6 border border-white border-opacity-20"
            >
              <h3 className="text-purple-200 text-sm font-semibold mb-2">Total Songs</h3>
              <p className="text-4xl font-bold text-white">{stats.total_songs}</p>
            </motion.div>

            {/* Total Sessions */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-white bg-opacity-10 backdrop-blur-lg rounded-xl p-6 border border-white border-opacity-20"
            >
              <h3 className="text-purple-200 text-sm font-semibold mb-2">Sessions</h3>
              <p className="text-4xl font-bold text-white">{stats.completed_sessions}/{stats.total_sessions}</p>
              <p className="text-purple-300 text-xs mt-2">completed</p>
            </motion.div>

            {/* Avg Rating */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="bg-white bg-opacity-10 backdrop-blur-lg rounded-xl p-6 border border-white border-opacity-20"
            >
              <h3 className="text-purple-200 text-sm font-semibold mb-2">Avg Rating</h3>
              <p className="text-4xl font-bold text-white">{stats.avg_rating}</p>
              <p className="text-yellow-300 text-xs mt-2">⭐ out of 5</p>
            </motion.div>
          </div>
        </div>
      )}

      {/* Users Tab */}
      {activeTab === 'users' && (
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white bg-opacity-10 backdrop-blur-lg rounded-xl p-6 border border-white border-opacity-20"
          >
            <h2 className="text-2xl font-bold text-white mb-6">User Management</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-purple-100">
                <thead className="border-b border-purple-400 border-opacity-20">
                  <tr>
                    <th className="text-left py-3 px-4">Email</th>
                    <th className="text-left py-3 px-4">Role</th>
                    <th className="text-left py-3 px-4">Joined</th>
                    <th className="text-left py-3 px-4">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((u) => (
                    <tr key={u.user_id} className="border-b border-purple-400 border-opacity-10 hover:bg-white hover:bg-opacity-5 transition">
                      <td className="py-3 px-4">{u.email}</td>
                      <td className="py-3 px-4">
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          u.role === 'admin'
                            ? 'bg-orange-500 bg-opacity-20 text-orange-200'
                            : 'bg-blue-500 bg-opacity-20 text-blue-200'
                        }`}>
                          {u.role}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-sm text-purple-300">
                        {new Date(u.created_at).toLocaleDateString()}
                      </td>
                      <td className="py-3 px-4">
                        {u.role === 'user' && user?.user_id !== u.user_id && (
                          <motion.button
                            whileHover={{ scale: 1.05 }}
                            onClick={() => handlePromoteUser(u.user_id)}
                            className="px-3 py-1 bg-green-500 hover:bg-green-600 text-white text-xs rounded transition"
                          >
                            Promote
                          </motion.button>
                        )}
                        {u.role === 'admin' && user?.user_id !== u.user_id && (
                          <motion.button
                            whileHover={{ scale: 1.05 }}
                            onClick={() => handleDemoteAdmin(u.user_id)}
                            className="px-3 py-1 bg-yellow-500 hover:bg-yellow-600 text-white text-xs rounded transition"
                          >
                            Demote
                          </motion.button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </motion.div>
        </div>
      )}

      {/* Songs Tab */}
      {activeTab === 'songs' && (
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white bg-opacity-10 backdrop-blur-lg rounded-xl p-6 border border-white border-opacity-20"
          >
            <h2 className="text-2xl font-bold text-white mb-6">Song Management</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-purple-100">
                <thead className="border-b border-purple-400 border-opacity-20">
                  <tr>
                    <th className="text-left py-3 px-4">Title</th>
                    <th className="text-left py-3 px-4">Artist</th>
                    <th className="text-left py-3 px-4">Rasa</th>
                    <th className="text-left py-3 px-4">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {songs.map((song) => (
                    <tr key={song._id} className="border-b border-purple-400 border-opacity-10 hover:bg-white hover:bg-opacity-5 transition">
                      <td className="py-3 px-4">{song.title}</td>
                      <td className="py-3 px-4 text-purple-300">{song.artist}</td>
                      <td className="py-3 px-4">
                        <span className="px-3 py-1 rounded-full text-xs font-semibold bg-purple-500 bg-opacity-20 text-purple-200">
                          {song.rasa}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <motion.button
                          whileHover={{ scale: 1.05 }}
                          onClick={() => handleDeleteSong(song._id)}
                          className="px-3 py-1 bg-red-500 hover:bg-red-600 text-white text-xs rounded transition"
                        >
                          Delete
                        </motion.button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;
