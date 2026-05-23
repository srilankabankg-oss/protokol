import { useState, useEffect } from 'react';

export interface ProtocolTask {
  id: string;
  number: number;
  code: string;
  description: string;
  responsible: string;
  controller: string;
  deadline: string;
  notes: string;
  subtasks: ProtocolTask[];
}

interface Props {
  meetingId: string;
  tasks: ProtocolTask[];
  onTasksChange: (tasks: ProtocolTask[]) => void;
  readOnly: boolean;
  participants: string[];
}

let counter = 0;
function makeTask(): ProtocolTask {
  counter++;
  return {
    id: 'tsk-' + Math.random().toString(36).slice(2, 11),
    number: counter,
    code: `TSK-${String(counter).padStart(3, '0')}`,
    description: '', responsible: '', controller: '',
    deadline: '', notes: '', subtasks: [],
  };
}

function TabularProtocol({ meetingId, tasks, onTasksChange, readOnly, participants }: Props) {
  const [localTasks, setLocalTasks] = useState<ProtocolTask[]>([]);
  const [dbPeople, setDbPeople] = useState<string[]>([]);

  useEffect(() => { setLocalTasks(tasks); }, [tasks]);

  // Load people from DB
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) return;
    fetch('/api/v1/admin/people', { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then(data => { if (Array.isArray(data)) setDbPeople(data.map(p => p.full_name)); })
      .catch(() => {});
  }, []);

  const allPeople = [...new Set([...participants, ...dbPeople])];

  function addTask() {
    const newTasks = [...localTasks, makeTask()];
    setLocalTasks(newTasks);
    onTasksChange(newTasks);
  }

  function setField(taskId: string, field: keyof ProtocolTask, value: string) {
    const updated = localTasks.map(t => (t.id === taskId ? { ...t, [field]: value } : t));
    setLocalTasks(updated);
    onTasksChange(updated);
  }

  function removeTask(taskId: string) {
    setLocalTasks(localTasks.filter(t => t.id !== taskId));
    onTasksChange(localTasks.filter(t => t.id !== taskId));
  }

  return (
    <div className="overflow-x-auto border rounded-lg mt-2">
      <table className="w-full border-collapse">
        <thead><tr className="bg-gray-100 text-xs font-medium text-gray-600">
          <th className="border px-2 py-2 w-8">№</th>
          <th className="border px-2 py-2 w-20">Код</th>
          <th className="border px-2 py-2">Описание задачи</th>
          <th className="border px-2 py-2 w-36">Ответственный</th>
          <th className="border px-2 py-2 w-36">Контролирующий</th>
          <th className="border px-2 py-2 w-28">Дата завершения</th>
          <th className="border px-2 py-2">Примечания</th>
          <th className="border px-2 py-2 w-10"></th>
        </tr></thead>
        <tbody>
          {localTasks.length === 0 && (
            <tr><td colSpan={8} className="text-center text-xs text-gray-400 py-4">
              Нет задач. Нажмите &quot;Добавить задачу&quot; или &quot;Обработать ИИ&quot;
            </td></tr>
          )}
          {localTasks.map((t, i) => (
            <tr key={t.id} className="border-b hover:bg-gray-50">
              <td className="border px-2 py-1 text-xs text-center">{i + 1}</td>
              <td className="border px-2 py-1 text-xs font-mono">{t.code}</td>
              <td className="border px-1 py-1">
                {readOnly ? <span className="text-xs">{t.description || '—'}</span> :
                  <input value={t.description} onChange={e => setField(t.id, 'description', e.target.value)}
                    className="w-full text-xs border-0 bg-transparent focus:outline-none" placeholder="Описание..." />}
              </td>
              <td className="border px-1 py-1">
                {readOnly ? <span className="text-xs">{t.responsible || '—'}</span> :
                  allPeople.length > 0 ? (
                    <select value={t.responsible} onChange={e => setField(t.id, 'responsible', e.target.value)}
                      className="w-full text-xs border-0 bg-transparent"><option value="">—</option>
                      {allPeople.map(p => <option key={p} value={p}>{p}</option>)}
                    </select>
                  ) : <input value={t.responsible} onChange={e => setField(t.id, 'responsible', e.target.value)}
                      className="w-full text-xs border-0 bg-transparent focus:outline-none" placeholder="Ответственный" />}
              </td>
              <td className="border px-1 py-1">
                {readOnly ? <span className="text-xs">{t.controller || '—'}</span> :
                  allPeople.length > 0 ? (
                    <select value={t.controller} onChange={e => setField(t.id, 'controller', e.target.value)}
                      className="w-full text-xs border-0 bg-transparent"><option value="">—</option>
                      {allPeople.map(p => <option key={p} value={p}>{p}</option>)}
                    </select>
                  ) : <input value={t.controller} onChange={e => setField(t.id, 'controller', e.target.value)}
                      className="w-full text-xs border-0 bg-transparent focus:outline-none" placeholder="Контролирующий" />}
              </td>
              <td className="border px-1 py-1">
                {readOnly ? <span className="text-xs">{t.deadline || '—'}</span> :
                  <input type="date" value={t.deadline} onChange={e => setField(t.id, 'deadline', e.target.value)}
                    className="w-full text-xs border-0 bg-transparent" />}
              </td>
              <td className="border px-1 py-1">
                {readOnly ? <span className="text-xs">{t.notes || '—'}</span> :
                  <input value={t.notes} onChange={e => setField(t.id, 'notes', e.target.value)}
                    className="w-full text-xs border-0 bg-transparent focus:outline-none" placeholder="..." />}
              </td>
              <td className="border px-1 py-1 text-center">
                {!readOnly && <button onClick={() => removeTask(t.id)} className="text-red-400 hover:text-red-600 text-xs">×</button>}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {!readOnly && (
        <button onClick={addTask} className="w-full py-2 text-blue-600 hover:bg-blue-50 text-sm border-t">
          + Добавить задачу
        </button>
      )}
    </div>
  );
}

export default TabularProtocol;
