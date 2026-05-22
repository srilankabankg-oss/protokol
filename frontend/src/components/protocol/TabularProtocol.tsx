import { useState } from 'react';

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
  participants: string[];
}

function makeTask(num: number): ProtocolTask {
  return {
    id: crypto.randomUUID(), number: num,
    code: `TSK-${String(num).padStart(3, '0')}`,
    description: '', responsible: '', controller: '',
    deadline: '', notes: '', subtasks: [],
  };
}

function TabularProtocol({ meetingId, tasks, onTasksChange, readOnly, participants }: Props) {
  function addTask() { onTasksChange([...tasks, makeTask(tasks.length + 1)]); }

  function setField(taskId: string, field: keyof ProtocolTask, value: string) {
    onTasksChange(tasks.map(t => t.id === taskId ? { ...t, [field]: value } : t));
  }

  function renderRow(t: ProtocolTask, i: number) {
    return (
      <tr key={t.id} className="border-b hover:bg-gray-50">
        <td className="border px-2 py-1 text-xs text-center w-8">{i + 1}</td>
        <td className="border px-2 py-1 text-xs font-mono w-16">{t.code}</td>
        <td className="border px-1 py-1">
          {readOnly ? <span className="text-xs">{t.description}</span> :
            <input value={t.description} onChange={e => setField(t.id, 'description', e.target.value)}
              className="w-full text-xs border-0 bg-transparent focus:outline-none" placeholder="Описание..." />}
        </td>
        <td className="border px-1 py-1 w-36">
          {!readOnly && participants.length > 0 ? (
            <select value={t.responsible} onChange={e => setField(t.id, 'responsible', e.target.value)} className="w-full text-xs border-0 bg-transparent">
              <option value="">—</option>
              {participants.map(p => <option key={p} value={p}>{p}</option>)}
            </select>
          ) : <span className="text-xs px-1">{t.responsible || '—'}</span>}
        </td>
        <td className="border px-1 py-1 w-36">
          {!readOnly && participants.length > 0 ? (
            <select value={t.controller} onChange={e => setField(t.id, 'controller', e.target.value)} className="w-full text-xs border-0 bg-transparent">
              <option value="">—</option>
              {participants.map(p => <option key={p} value={p}>{p}</option>)}
            </select>
          ) : <span className="text-xs px-1">{t.controller || '—'}</span>}
        </td>
        <td className="border px-1 py-1 w-28">
          {readOnly ? <span className="text-xs">{t.deadline}</span> :
            <input type="date" value={t.deadline} onChange={e => setField(t.id, 'deadline', e.target.value)} className="w-full text-xs border-0 bg-transparent" />}
        </td>
        <td className="border px-1 py-1">
          {readOnly ? <span className="text-xs">{t.notes}</span> :
            <input value={t.notes} onChange={e => setField(t.id, 'notes', e.target.value)} className="w-full text-xs border-0 bg-transparent focus:outline-none" placeholder="..." />}
        </td>
      </tr>
    );
  }

  return (
    <div className="overflow-x-auto border rounded-lg mt-2">
      <table className="w-full border-collapse">
        <thead>
          <tr className="bg-gray-100 text-xs font-medium text-gray-600">
            <th className="border px-2 py-2 w-8">№</th>
            <th className="border px-2 py-2 w-16">Код</th>
            <th className="border px-2 py-2">Описание задачи</th>
            <th className="border px-2 py-2 w-36">Ответственный</th>
            <th className="border px-2 py-2 w-36">Контролирующий</th>
            <th className="border px-2 py-2 w-28">Дата завершения</th>
            <th className="border px-2 py-2">Примечания</th>
          </tr>
        </thead>
        <tbody>
          {tasks.length === 0 && (
            <tr><td colSpan={7} className="text-center text-xs text-gray-400 py-4">Нет задач. Нажмите "Добавить задачу" или "Обработать ИИ"</td></tr>
          )}
          {tasks.map((t, i) => renderRow(t, i))}
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
