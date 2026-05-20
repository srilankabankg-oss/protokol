import { create } from 'zustand';
import type { User } from '../types';
import * as api from '../api/client';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string, role: string) => Promise<void>;
  logout: () => void;
  loadFromStorage: () => void;
}

const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,

  login: async (email, password) => {
    const data = await api.login(email, password);
    localStorage.setItem('access_token', data.access_token);
    set({ token: data.access_token, isAuthenticated: true });
  },

  register: async (name, email, password, role) => {
    await api.register(name, email, password, role);
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    set({ token: null, user: null, isAuthenticated: false });
  },

  loadFromStorage: () => {
    const token = localStorage.getItem('access_token');
    if (token) set({ token, isAuthenticated: true });
  },
}));

export default useAuthStore;