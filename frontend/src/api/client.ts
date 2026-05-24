import axios from 'axios';
import type {
  AIInsights,
  MeetingCreatePayload,
  MeetingCreateResponse,
  MeetingListItem,
  MeetingWorkspace,
  Organization,
  Person,
  Contract,
  RaciResponse,
  TaskResponse,
  TokenResponse,
  User,
} from '../types';

const api = axios.create({ baseURL: '/api/v1' });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

let isRefreshing = false;
let refreshPromise: Promise<string | null> | null = null;

api.interceptors.response.use(
  (r) => r,
  async (error) => {
    if (error.response?.status === 401 && error.config && !error.config._retry) {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken && !isRefreshing) {
        error.config._retry = true;
        isRefreshing = true;
        try {
          const { data } = await axios.post('/api/v1/auth/refresh', { refresh_token: refreshToken });
          localStorage.setItem('access_token', data.access_token);
          localStorage.setItem('refresh_token', data.refresh_token);
          error.config.headers.Authorization = `Bearer ${data.access_token}`;
          isRefreshing = false;
          return api(error.config);
        } catch {
          isRefreshing = false;
        }
      }
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  },
);

export const login = async (email: string, password: string): Promise<TokenResponse> => {
  const { data } = await api.post('/auth/login', { email, password });
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('refresh_token', data.refresh_token);
  return data;
};

export const register = async (
  name: string, email: string, password: string, role: string,
): Promise<User> => {
  const { data } = await api.post('/auth/register', { name, email, password, role });
  return data;
};

export const getMeetings = async (params?: Record<string, string>): Promise<MeetingListItem[]> => {
  const { data } = await api.get('/meetings', { params });
  return data;
};

export const createMeeting = async (payload: MeetingCreatePayload): Promise<MeetingCreateResponse> => {
  const { data } = await api.post('/meetings', payload);
  return data;
};

export const getWorkspace = async (id: string): Promise<MeetingWorkspace> => {
  const { data } = await api.get(`/meetings/${id}/workspace`);
  return data;
};

export const updateContent = async (id: string, content_markdown: string): Promise<{ version: number }> => {
  const { data } = await api.patch(`/meetings/${id}/content`, { content_markdown });
  return data;
};

export const startWorkMeeting = async (id: string) => {
  const { data } = await api.post(`/meetings/${id}/start-work`);
  return data;
};

export const finalizeMeeting = async (id: string) => {
  const { data } = await api.post(`/meetings/${id}/finalize`);
  return data;
};

export const approveMeeting = async (id: string) => {
  const { data } = await api.post(`/meetings/${id}/approve`);
  return data;
};

export const createTask = async (payload: { meeting_id: string; description: string; organization_links?: string[] }): Promise<TaskResponse> => {
  const { data } = await api.post('/tasks', payload);
  return data;
};

export const getRaci = async (taskId: string): Promise<RaciResponse> => {
  const { data } = await api.get(`/tasks/${taskId}/raci`);
  return data;
};

export const updateRaci = async (taskId: string, assignments: { user_id: string; role: string }[]): Promise<RaciResponse> => {
  const { data } = await api.put(`/tasks/${taskId}/raci`, { assignments });
  return data;
};

export const escalateTask = async (taskId: string, payload: { target_meeting_type: string; reason: string }) => {
  const { data } = await api.post(`/tasks/${taskId}/escalate`, payload);
  return data;
};

export const getDependencies = async (taskId: string) => {
  const { data } = await api.get(`/tasks/${taskId}/dependencies`);
  return data;
};

export const getAIInsights = async (meetingId: string): Promise<AIInsights> => {
  const { data } = await api.get(`/meetings/${meetingId}/ai-insights`);
  return data;
};

// ── Admin API ──

export const getOrganizations = async (): Promise<Organization[]> => {
  const { data } = await api.get('/admin/organizations');
  return data;
};

export const createOrganization = async (payload: Partial<Organization>): Promise<Organization> => {
  const { data } = await api.post('/admin/organizations', payload);
  return data;
};

export const getPeople = async (): Promise<Person[]> => {
  const { data } = await api.get('/admin/people');
  return data;
};

export const createPerson = async (payload: Partial<Person>): Promise<Person> => {
  const { data } = await api.post('/admin/people', payload);
  return data;
};

export const getContracts = async (): Promise<Contract[]> => {
  const { data } = await api.get('/admin/contracts');
  return data;
};

export const createContract = async (payload: Partial<Contract>): Promise<Contract> => {
  const { data } = await api.post('/admin/contracts', payload);
  return data;
};

export const getUsers = async (): Promise<User[]> => {
  const { data } = await api.get('/admin/users');
  return data;
};