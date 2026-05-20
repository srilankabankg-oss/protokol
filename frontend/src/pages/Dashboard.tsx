import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import { ru } from 'date-fns/locale';
import { getMeetings, createMeeting } from '../api/client';
import useAuthStore from '../store/authStore';
import type { MeetingListItem } from '../types';

const LEVEL_LABELS: Record<string, string> = {
  strategic: 'Стратегический',
  coordination: 'Координационный',
  operational: 'Оперативный',
  situational: 'Проблемный',
};

const LEVEL_COLORS: Record<string, string> = {
  strategic: 'bg-amber-100 text-amber-800',
  coordination: 'bg-purple-100 text-purple-800',
  operational: 'bg-blue-100 text-blue-800',
  situational: 'bg-red-100 text-red-800',
};

const STATUS_LABELS: Record<string, string> = {
  preparation: 'Подготовка',
  in_progress: 'В процессе',
  on_approval: 'На согласовании',
  approved: 'Утверждено',
};

const STATUS_COLORS: Record<string, string> = {
  preparation: 'text-gray-500',
  in_progress: 'text-blue-600',
  on_approval: 'text-orange-500',
  approved: 'text-green-600',
};

function Dashboard() {
  const [meetings, setMeetings] = useState<MeetingListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [levelFilter, setLevelFilter] = useState('');
  const [showCreate, setShowCreate] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newLevel, setNewLevel] = useState('operational');
const [creating, setCreating] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);
  const navigate = useNavigate();
  const auth = useAuthStore();

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const params: Record<string, string> = {};
        if (levelFilter) params.level = levelFilter;
        const data = await getMeetings(params);
        if (!cancelled) setMeetings(data);
      } catch (e: any) {
        if (!cancelled) setError('Ошибка загрузки');
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, [levelFilter, refreshKey]);

  async function handleCreate() {
    if (!newTitle.trim()) return;
    setCreating(true);
    try {
      await createMeeting({
        title: newTitle.trim(),
        level: newLevel as MeetingListItem['level'],
        agenda_items: [],
      });
      setShowCreate(false);
      setNewTitle('');
      setRefreshKey(k => k + 1);
    } catch {
      setError('Ошибка создания совещания');
    } finally {
      setCreating(false);
    }
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Центр управления совещаниями</h1>
        <p className="text-gray-500 mt-1">Книга добрых дел</p>
      </div>

      <div className="flex justify-end mb-4">
        <button
          onClick={() => { auth.logout(); navigate('/login'); }}
          className="px-3 py-1.5 text-sm text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
        >
          Выйти
        </button>
      </div>

      <div className="flex flex-wrap gap-3 mb-6 items-center">
        <select
          value={levelFilter}
          onChange={(e) => setLevelFilter(e.target.value)}
          className="border rounded-lg px-3 py-2 text-sm bg-white"
        >
          <option value="">Все уровни</option>
          {Object.entries(LEVEL_LABELS).map(([k, v]) => (
            <option key={k} value={k}>{v}</option>
          ))}
        </select>

        <button
          onClick={() => setShowCreate(true)}
          className="ml-auto px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium"
        >
          + Создать совещание
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg p-4 mb-4">
          {error}
          <button onClick={() => setRefreshKey(k => k + 1)} className="ml-4 underline">Повторить</button>
        </div>
      )}

      {showCreate && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md shadow-lg">
            <h2 className="text-lg font-semibold mb-4">Новое совещание</h2>
            <input
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              placeholder="Название совещания"
              className="w-full border rounded-lg px-3 py-2 text-sm mb-3"
              autoFocus
            />
            <select
              value={newLevel}
              onChange={(e) => setNewLevel(e.target.value)}
              className="w-full border rounded-lg px-3 py-2 text-sm mb-4"
            >
              {Object.entries(LEVEL_LABELS).map(([k, v]) => (
                <option key={k} value={k}>{v}</option>
              ))}
            </select>
            <div className="flex gap-2 justify-end">
              <button
                onClick={() => setShowCreate(false)}
                className="px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg"
              >
                Отмена
              </button>
              <button
                onClick={handleCreate}
                disabled={creating || !newTitle.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm disabled:opacity-50"
              >
                {creating ? 'Создание...' : 'Создать'}
              </button>
            </div>
          </div>
        </div>
      )}

      {loading && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map(i => (
            <div key={i} className="bg-white rounded-xl p-5 shadow-sm animate-pulse h-36" />
          ))}
        </div>
      )}

      {!loading && !error && meetings.length === 0 && (
        <div className="text-center py-16 text-gray-400">
          <p className="text-lg">Нет совещаний</p>
          <p className="text-sm mt-1">Создайте первое совещание</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {meetings.map((m) => (
          <div
            key={m.meeting_id}
            onClick={() => navigate(`/meetings/${m.meeting_id}`)}
            className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md hover:border-blue-200 cursor-pointer transition-all"
          >
            <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${LEVEL_COLORS[m.level] || ''}`}>
              {LEVEL_LABELS[m.level] || m.level}
            </span>
            <h3 className="mt-2 font-semibold text-gray-900 truncate">{m.title}</h3>
            <div className={`text-sm mt-1 ${STATUS_COLORS[m.status] || ''}`}>
              {STATUS_LABELS[m.status] || m.status}
            </div>
            <div className="text-xs text-gray-400 mt-2">
              {m.date ? format(new Date(m.date), 'dd.MM.yyyy HH:mm', { locale: ru }) : '—'}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Dashboard;