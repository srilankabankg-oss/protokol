import { useState, useEffect } from 'react';
import { getRaci, updateRaci } from '../../api/client';
import type { RaciAssignment, RaciResponse, RaciRoleType } from '../../types';

const RACI_ROLES: { key: RaciRoleType; label: string; desc: string; color: string }[] = [
  { key: 'R', label: 'R', desc: 'Исполнитель', color: 'bg-blue-100 text-blue-800' },
  { key: 'A', label: 'A', desc: 'Ответственный', color: 'bg-red-100 text-red-800' },
  { key: 'C', label: 'C', desc: 'Консультант', color: 'bg-purple-100 text-purple-800' },
  { key: 'I', label: 'I', desc: 'Информируемый', color: 'bg-gray-100 text-gray-700' },
];

interface Props {
  taskId: string;
  onClose: () => void;
}

function RACIGrid({ taskId, onClose }: Props) {
  const [raci, setRaci] = useState<RaciResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [editingAssignments, setEditingAssignments] = useState<{ user_id: string; role: RaciRoleType }[]>([]);

  useEffect(() => { fetchRaci(); }, [taskId]);

  async function fetchRaci() {
    setLoading(true);
    try {
      const data = await getRaci(taskId);
      setRaci(data);
      setEditingAssignments(data.assignments.map(a => ({ user_id: a.user_id, role: a.role as RaciRoleType })));
      setError(null);
    } catch {
      setError('Ошибка загрузки RACI');
    } finally {
      setLoading(false);
    }
  }

  function handleRoleChange(index: number, newRole: RaciRoleType) {
    const updated = [...editingAssignments];
    updated[index] = { ...updated[index], role: newRole };
    setEditingAssignments(updated);
  }

  async function handleSave() {
    setSaving(true);
    setError(null);
    try {
      const data = await updateRaci(taskId, editingAssignments.map(a => ({
        user_id: a.user_id,
        role: a.role,
      })));
      setRaci(data);
      setEditMode(false);
    } catch (e: any) {
      const detail = e.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : (detail?.message || 'Ошибка валидации RACI'));
    } finally {
      setSaving(false);
    }
  }

  function getAcount(assignments: { role: string }[]) {
    return assignments.filter(a => a.role === 'A').length;
  }

  if (loading) {
    return <div className="p-4 text-center text-gray-400">Загрузка...</div>;
  }

  if (!raci) {
    return <div className="p-4 text-center text-red-500">{error}</div>;
  }

  const currentAssignments = editMode ? editingAssignments : raci.assignments;
  const aCount = getAcount(currentAssignments);
  const isValid = aCount === 1;

  return (
    <div className="bg-white rounded-xl border shadow-lg max-w-lg w-full mx-auto p-5">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">Матрица RACI</h2>
        <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl leading-none">&times;</button>
      </div>

      {!isValid && (
        <div className={`text-xs rounded-lg p-2 mb-3 ${aCount > 1 ? 'bg-red-50 text-red-700' : 'bg-yellow-50 text-yellow-700'}`}>
          {aCount > 1 ? `⚠️ ${aCount} роли Accountable — должна быть одна` : '⚠️ Отсутствует роль Accountable (A)'}
        </div>
      )}

      {error && (
        <div className="bg-red-50 text-red-700 text-xs rounded-lg p-2 mb-3">{error}</div>
      )}

      <div className="mb-3 flex gap-2 flex-wrap">
        {RACI_ROLES.map(r => (
          <span key={r.key} className={`px-2 py-0.5 rounded text-xs ${r.color}`}>
            {r.key} = {r.desc}
          </span>
        ))}
      </div>

      <table className="w-full text-sm">
        <thead>
          <tr className="border-b text-left text-gray-500 text-xs">
            <th className="pb-2">Пользователь</th>
            <th className="pb-2">Роль</th>
            {editMode && <th className="pb-2 w-20">Изменить</th>}
          </tr>
        </thead>
        <tbody>
          {currentAssignments.map((a, i) => (
            <tr key={i} className="border-b last:border-0">
              <td className="py-2 pr-2">
                <span className="text-gray-700">{a.name || a.user_id.slice(0, 8)}</span>
              </td>
              <td className="py-2">
                <span className={`px-2 py-0.5 rounded text-xs ${
                  a.role === 'A' ? 'bg-red-100 text-red-800' :
                  a.role === 'R' ? 'bg-blue-100 text-blue-800' :
                  a.role === 'C' ? 'bg-purple-100 text-purple-800' :
                  'bg-gray-100 text-gray-700'
                }`}>
                  {a.role}
                </span>
              </td>
              {editMode && (
                <td className="py-2">
                  <select
                    value={a.role}
                    onChange={(e) => handleRoleChange(i, e.target.value as RaciRoleType)}
                    className="text-xs border rounded px-1 py-0.5"
                  >
                    {RACI_ROLES.map(r => (
                      <option key={r.key} value={r.key}>{r.key} — {r.desc}</option>
                    ))}
                  </select>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>

      {currentAssignments.length === 0 && (
        <p className="text-center text-gray-400 text-sm py-4">Нет назначений RACI</p>
      )}

      <div className="flex justify-end gap-2 mt-4">
        {editMode ? (
          <>
            <button onClick={() => { setEditMode(false); setEditingAssignments(raci.assignments.map(a => ({ user_id: a.user_id, role: a.role as RaciRoleType }))); }} className="px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded">
              Отмена
            </button>
            <button onClick={handleSave} disabled={saving} className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50">
              {saving ? 'Сохранение...' : 'Сохранить'}
            </button>
          </>
        ) : (
          <button onClick={() => setEditMode(true)} className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700">
            Редактировать
          </button>
        )}
      </div>
    </div>
  );
}

export default RACIGrid;