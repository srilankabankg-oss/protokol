import { useState, useEffect } from 'react';

interface ProtocolTask {
  id: string;
  number: number;
  code: string;
  description: string;
  responsible: string;
  controller: string;
  deadline: string;
  notes: string;
  parent_id: string | null;
  subtasks: ProtocolTask[];
}

interface Props {
  meetingId: string;
  tasks: ProtocolTask[];
  onTasksChange: (tasks: ProtocolTask[]) => void;
  readOnly: boolean;
}

function TabularProtocol({ meetingId, tasks, onTasksChange, readOnly }: Props) {
  const [editingCell, setEditingCell] = useState<{taskId: string; field: string} | null>(null);
  const [editValue, setEditValue] = useState('');

  function generateCode(index: number): string {
    return `TSK-${String(index + 1).padStart(3, '0')}`;
  }

  function addTask(parentId: string | null = null) {
    const newTask: ProtocolTask = {
      id: crypto.randomUUID(),
      number: tasks.length + 1,
      code: generateCode(tasks.length),
      description: '',
      responsible: '',
      controller: '',
      deadline: '',
      notes: '',
      parent_id: parentId,
      subtasks: [],
    };
    onTasksChange([...tasks, newTask]);
  }

  function updateTask(taskId: string, field: string, value: string) {
    const updated = tasks.map(t => t.id === taskId ? { ...t, [field]: value } : t);
    onTasksChange(updated);
    setEditingCell(null);
  }

  function startEdit(taskId: string, field: string, currentValue: string) {
    if (readOnly) return;
    setEditingCell({ taskId, field });
    setEditValue(currentValue);
  }

  function deleteTask(taskId: string) {
    onTasksChange(tasks.filter(t => t.id !== taskId));
  }

  const cols = [
    { key: 'number', label: '№', width: 'w-10' },
    { key: 'code', label: 'Код', width: 'w-20' },
    { key: 'description', label: 'Описание задачи', width: 'min-w-[200px]' },
    { key: 'responsible', label: 'Ответственный', width: 'w-32' },
    { key: 'controller', label: 'Контролирующий', width: 'w-32' },
    { key: 'deadline', label: 'Дата завершения', width: 'w-28' },
    { key: 'notes', label: 'Примечания', width: 'w-32' },
    { key: 'actions', label: '', width: 'w-24' },
  ];

  const editableFields = ['description', 'responsible', 'controller', 'deadline', 'notes'];

  return (
    <div className="overflow-x-auto border rounded-lg">
      <table className="w-full text-sm">
        <thead className="bg-gray-50 border-b">
          <tr>
            {cols.map(c => (
              <th key={c.key} className={`px-2 py-2 text-left text-xs font-medium text-gray-500 ${c.width}`}>{c.label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {tasks.map((task, i) => (
            <tr key={task.id} className="border-b hover:bg-gray-50">
              <td className="px-2 py-2 text-gray-400 text-xs">{i + 1}</td>
              <td className="px-2 py-2 font-mono text-xs text-gray-500">{task.code}</td>
              {editableFields.map(field => (
                <td key={field} className="px-2 py-1">
                  {editingCell?.taskId === task.id && editingCell?.field === field ? (
                    <input
                      autoFocus
                      value={editValue}
                      onChange={e => setEditValue(e.target.value)}
                      onBlur={() => updateTask(task.id, field, editValue)}
                      onKeyDown={e => { if (e.key === 'Enter') updateTask(task.id, field, editValue); if (e.key === 'Escape') setEditingCell(null); }}
                      className="w-full border rounded px-1 py-0.5 text-xs"
                    />
                  ) : (
                    <div
                      onClick={() => startEdit(task.id, field, (task as any)[field])}
                      className={`text-xs px-1 py-0.5 min-h-[20px] rounded ${readOnly ? 'cursor-default' : 'cursor-pointer hover:bg-blue-50'} ${!task[field as keyof ProtocolTask] ? 'text-gray-300 italic' : 'text-gray-700'}`}
                    >
                      {(task as any)[field] || '—'}
                    </div>
                  )}
                </td>
              ))}
              <td className="px-2 py-2">
                {!readOnly && (
                  <div className="flex gap-1">
                    <button onClick={() => addTask(task.id)} title="Подзадача" className="text-xs text-blue-500 hover:text-blue-700">↳</button>
                    <button onClick={() => deleteTask(task.id)} className="text-xs text-red-400 hover:text-red-600">×</button>
                  </div>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {!readOnly && (
        <div className="p-2 border-t">
          <button onClick={() => addTask()} className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700">
            + Добавить задачу
          </button>
        </div>
      )}
    </div>
  );
}

export default TabularProtocol;
export type { ProtocolTask };