import { useEffect, useRef, useCallback, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import useMeetingStore from '../store/meetingStore';
import AIPanel from '../components/ai/AIPanel';
import NavBar from '../components/ui/NavBar';
import ApprovalStepper from '../components/ui/ApprovalStepper';
import ExportButtons from '../components/ui/ExportButtons';
import TabularProtocol, { type ProtocolTask } from '../components/protocol/TabularProtocol';

function MeetingEditor() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const store = useMeetingStore();
  const saveTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (id) store.loadWorkspace(id);
    return () => { store.reset(); };
  }, [id]);

  const autosave = useCallback(() => {
    if (store.isDirty) store.saveContent();
  }, [store.isDirty]);

  useEffect(() => {
    saveTimerRef.current = setInterval(autosave, 10000);
    return () => { if (saveTimerRef.current) clearInterval(saveTimerRef.current); };
  }, [autosave]);

  const [protocolTasks, setProtocolTasks] = useState<ProtocolTask[]>([]);
  const [showAddParticipant, setShowAddParticipant] = useState<boolean>(false);
  const [newParticipantName, setNewParticipantName] = useState<string>();

  if (store.isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  if (store.error || !store.meeting) {
    return (
      <div className="flex items-center justify-center h-screen text-red-500">
        {store.error || 'Встреча не найдена'}
      </div>
    );
  }

  const { meeting } = store;
  const STATUS_LABELS: Record<string, string> = {
    preparation: 'Подготовка', in_progress: 'В процессе',
    on_approval: 'На согласовании', approved: 'Утверждено',
  };

  const canEdit = meeting.status !== 'approved';
  const canApprove = meeting.status === 'on_approval';
  const participants = meeting.participants.map(p => p.name).filter(Boolean);

  async function handleAIProcess() {
    await store.saveContent();
    await store.triggerAI();
  }

  return (
    <>
      <NavBar />
      <div className="flex flex-col h-screen">
        <header className="bg-white border-b px-4 py-3 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3 text-sm text-gray-500">
            {meeting.breadcrumbs.map((crumb, i) => (
              <span key={i}>
                {i > 0 && <span className="mx-1">›</span>}
                {crumb}
              </span>
            ))}
          </div>
          <div className="flex items-center gap-3">
            <button onClick={() => { navigate('/login'); }} className="text-xs text-gray-400 hover:text-red-500 px-2 py-1 rounded hover:bg-red-50">
              Выйти
            </button>
            <span className={`px-2 py-1 rounded text-xs font-medium ${
              meeting.status === 'preparation' ? 'bg-gray-100 text-gray-600' :
              meeting.status === 'in_progress' ? 'bg-blue-100 text-blue-700' :
              meeting.status === 'on_approval' ? 'bg-orange-100 text-orange-700' :
              'bg-green-100 text-green-700'
            }`}>
              {STATUS_LABELS[meeting.status]}
            </span>
            <ExportButtons meetingId={meeting.meeting_id} />
            <span className="text-xs text-gray-400">v{store.version}</span>

            {canEdit && (
              <button onClick={handleAIProcess} className="px-3 py-1.5 bg-purple-600 text-white rounded text-sm hover:bg-purple-700">
                🤖 Обработать ИИ
              </button>
            )}
            {meeting.status === 'preparation' && (
              <button onClick={store.startWork} className="px-3 py-1.5 bg-blue-600 text-white rounded text-sm hover:bg-blue-700">
                Начать ведение
              </button>
            )}
            {meeting.status === 'in_progress' && (
              <button onClick={store.finalize} className="px-3 py-1.5 bg-orange-500 text-white rounded text-sm hover:bg-orange-600">
                Завершить
              </button>
            )}
            {canApprove && (
              <button onClick={store.approve} className="px-3 py-1.5 bg-green-600 text-white rounded text-sm hover:bg-green-700">
                Утвердить
              </button>
            )}
          </div>
        </header>

        <div className="bg-white border-b px-4 py-2 shrink-0">
          <ApprovalStepper currentStatus={meeting.status} />
        </div>

        <div className="flex flex-1 overflow-hidden">
          <aside className="w-64 bg-white border-r p-4 overflow-y-auto shrink-0 hidden md:block">
            <h3 className="font-semibold text-sm text-gray-700 mb-3">Участники</h3>
            <button onClick={() => setShowAddParticipant(!showAddParticipant)} className="mb-3 px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700">
              + Добавить участника
            </button>
          {showAddParticipant && (
            <div className="mb-3 flex gap-2">
              <input value={newParticipantName} onChange={e => setNewParticipantName(e.target.value)} placeholder="Имя участника" className="flex-1 border rounded px-2 py-1 text-xs" />
              <button onClick={() => { setNewParticipantName(''); setShowAddParticipant(false); }} className="px-2 py-1 bg-blue-600 text-white rounded text-xs">OK</button>
            </div>
          )}
            <ul className="space-y-2 mb-6">
              {meeting.participants.map(p => (
                <li key={p.user_id} className="flex items-center gap-2 text-sm">
                  <span className={`w-2 h-2 rounded-full ${p.is_present ? 'bg-green-500' : 'bg-red-400'}`} />
                  <span className="truncate flex-1">{p.name}</span>
                  <span className={`text-xs px-1.5 py-0.5 rounded ${
                    p.role === 'chairman' ? 'bg-amber-100 text-amber-700' :
                    p.role === 'secretary' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600'
                  }`}>
                    {p.role === 'chairman' ? 'Пред.' : p.role === 'secretary' ? 'Секр.' : 'Уч.'}
                  </span>
                </li>
              ))}
            </ul>

            <h3 className="font-semibold text-sm text-gray-700 mb-3">Повестка</h3>
            <ol className="space-y-1 text-sm">
              {meeting.agenda.map(a => (
                <li key={a.agenda_id} className="flex items-start gap-2">
                  <span className="text-gray-400 mt-0.5">{a.position}.</span>
                  <span className={a.is_completed ? 'line-through text-gray-400' : ''}>{a.title}</span>
                </li>
              ))}
</ol>
        </aside>

          <main className="flex-1 flex flex-col min-w-0">
            <div className="flex-1 p-4 overflow-auto">
              <textarea
                value={store.contentMarkdown}
                onChange={(e) => store.setContent(e.target.value)}
                disabled={!canEdit}
                placeholder="Начните вводить текст протокола...\n\n## СЛУШАЛИ\n\n## ВЫСТУПИЛИ\n\n## ПОСТАНОВИЛИ"
                className="w-full h-48 resize-y font-mono text-sm p-4 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-300 disabled:bg-gray-50 disabled:text-gray-500 mb-4"
              />
              <h3 className="text-sm font-semibold text-gray-700 mb-2">📋 Протокол (табличная форма)</h3>
              <TabularProtocol
                tasks={protocolTasks}
                onTasksChange={setProtocolTasks}
                readOnly={!canEdit}
                participants={participants}
                meetingId={meeting.meeting_id}
              />
            </div>
            <div className="bg-gray-50 border-t px-4 py-1.5 flex items-center justify-between text-xs text-gray-400 shrink-0">
              <span>{store.isDirty ? '● Не сохранено' : '✓ Сохранено'}</span>
              <span>версия {store.version}</span>
            </div>
          </main>

          <AIPanel meetingId={meeting.meeting_id} />
        </div>
      </div>
    </>
  );
}

export default MeetingEditor;