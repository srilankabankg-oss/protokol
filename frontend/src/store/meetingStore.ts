import { create } from 'zustand';
import type { MeetingWorkspace } from '../types';
import * as api from '../api/client';

interface MeetingState {
  meeting: MeetingWorkspace | null;
  isLoading: boolean;
  error: string | null;
  contentMarkdown: string;
  isDirty: boolean;
  version: number;

  loadWorkspace: (id: string) => Promise<void>;
  setContent: (markdown: string) => void;
  saveContent: () => Promise<void>;
  startWork: () => Promise<void>;
  triggerAI: () => Promise<void>;
  finalize: () => Promise<void>;
  approve: () => Promise<void>;
  reset: () => void;
}

const useMeetingStore = create<MeetingState>((set, get) => ({
  meeting: null,
  isLoading: false,
  error: null,
  contentMarkdown: '',
  isDirty: false,
  version: 1,

  loadWorkspace: async (id) => {
    set({ isLoading: true, error: null });
    try {
      const ws = await api.getWorkspace(id);
      set({
        meeting: ws,
        contentMarkdown: ws.content_markdown || '',
        isLoading: false,
      });
    } catch (e: any) {
      set({ error: e.message || 'Failed to load', isLoading: false });
    }
  },

  setContent: (markdown: string) => {
    set({ contentMarkdown: markdown, isDirty: true });
  },

  saveContent: async () => {
    const { meeting, contentMarkdown, isDirty } = get();
    if (!meeting || !isDirty) return;
    try {
      const result = await api.updateContent(meeting.meeting_id, contentMarkdown);
      set({ isDirty: false, version: result.version });
    } catch (e) {
      console.error('Autosave failed', e);
    }
  },

  startWork: async () => {
    const { meeting } = get();
    if (!meeting) return;
    await api.startWorkMeeting(meeting.meeting_id);
    await get().loadWorkspace(meeting.meeting_id);
  },

  triggerAI: async () => {
    const { meeting, contentMarkdown } = get();
    if (!meeting) return;
    try {
      await api.updateContent(meeting.meeting_id, contentMarkdown);
      set({ isDirty: false });
    } catch (e) {
      console.error('AI failed', e);
    }
  },

  finalize: async () => {
    const { meeting } = get();
    if (!meeting) return;
    await api.finalizeMeeting(meeting.meeting_id);
    await get().loadWorkspace(meeting.meeting_id);
  },

  approve: async () => {
    const { meeting } = get();
    if (!meeting) return;
    await api.approveMeeting(meeting.meeting_id);
    await get().loadWorkspace(meeting.meeting_id);
  },

  reset: () => set({
    meeting: null, contentMarkdown: '', isDirty: false,
    error: null, isLoading: false, version: 1,
  }),
}));

export default useMeetingStore;