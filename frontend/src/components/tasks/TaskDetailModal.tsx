import { useState, useEffect } from 'react';
import { escalateTask, getDependencies, getRaci, createTask } from '../../api/client';
import RACIGrid from '../raci/RACIGrid';
import type { TaskResponse } from '../../types';

interface Props {
  taskId: string;
  onClose: () => void;
  onRefresh?: () => void;
}

function TaskDetailModal({ taskId, onClose, onRefresh }: Props) {
  const [task, setTask] = useState<TaskResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [escalating, setEscalating] = useState(false);
  const [escalateTarget, setEscalateTarget] = useState('coordination');
  const [escalateReason, setEscalateReason] = useState('');
  const [showEscalate, setShowEscalate] = useState(false);
  const [showRaci, setShowRaci] = useState(false);
  const [deps, setDeps] = useState<{ previous_task_id?: string; next_task_id?: string } | null>(null);

  useEffect(() => {
    fetchTask();
  }, [taskId]);

  async function fetchTask() {
    setLoading(true);
    try {
      const [raciData, depData] = await Promise.all([
        getRaci(taskId),
        getDependencies(taskId),
      ]);
      setTask({
        task_id: taskId,
        task_number: '',
        description: '',
        workflow_stage: 'to_do',
        raci_valid: raciData.is_valid,
        created_at: '',
      });
      setDeps(depData.graph_edges);
    } catch {
      setLoading(false);
    }
  }

  async function handleEscalate() {
    setEscalating(true);
    try {
      await escalateTask(taskId, {
        target_meeting_type: escalateTarget,
        reason: escalateReason,
      });
      setShowEscalate(false);
      onRefresh?.();
      onClose();
    } catch (e: any) {
      alert(e.response?.data?.detail || 'Ошибка эскалации');
    } finally {
      setEscalating(false);
    }
  }

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50">
        <div className="bg-white rounded-xl p-6">Загрузка...</div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div className="bg-white rounded-xl shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
        <div className="p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Детали задачи</h2>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-xl">&times;</button>
          </div>

          {task && (
            <div className="space-y-4">
              <div>
                <span className="text-xs text-gray-400">Номер</span>
                <p className="font-mono text-sm">{task.task_number || taskId.slice(0, 12)}</p>
              </div>
              <div>
                <span className="text-xs text-gray-400">Статус</span>
                <p className="text-sm">{task.workflow_stage}</p>
              </div>

              {deps && (
                <div>
                  <span className="text-xs text-gray-400">Цепочка зависимостей</span>
                  <div className="mt-2 flex items-center gap-2 text-xs">
                    {deps.previous_task_id ? (
                      <span className="bg-gray-100 px-2 py-1 rounded">← {deps.previous_task_id.slice(0, 8)}</span>
                    ) : (
                      <span className="text-gray-300">Начало</span>
                    )}
                    <span className="text-blue-500">●</span>
                    {deps.next_task_id ? (
                      <span className="bg-gray-100 px-2 py-1 rounded">{deps.next_task_id.slice(0, 8)} →</span>
                    ) : (
                      <span className="text-gray-300">Конец</span>
                    )}
                  </div>
                </div>
              )}

              <div className="flex flex-wrap gap-2">
                <button onClick={() => setShowRaci(true)} className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700">
                  Матрица RACI
                </button>
                <button onClick={() => setShowEscalate(!showEscalate)} className="px-3 py-1.5 text-sm bg-orange-500 text-white rounded hover:bg-orange-600">
                  Эскалировать
                </button>
              </div>

              {showEscalate && (
                <div className="bg-gray-50 rounded-lg p-4 space-y-3">
                  <h3 className="text-sm font-medium">Эскалация вопроса</h3>
                  <select
                    value={escalateTarget}
                    onChange={(e) => setEscalateTarget(e.target.value)}
                    className="w-full border rounded px-2 py-1 text-sm"
                  >
                    <option value="coordination">Координационный уровень</option>
                    <option value="strategic">Стратегический уровень</option>
                  </select>
                  <textarea
                    value={escalateReason}
                    onChange={(e) => setEscalateReason(e.target.value)}
                    placeholder="Причина эскалации..."
                    className="w-full border rounded px-2 py-1 text-sm h-16 resize-none"
                  />
                  <div className="flex gap-2">
                    <button onClick={() => setShowEscalate(false)} className="px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded">
                      Отмена
                    </button>
                    <button onClick={handleEscalate} disabled={escalating} className="px-3 py-1.5 text-sm bg-orange-600 text-white rounded hover:bg-orange-700 disabled:opacity-50">
                      {escalating ? 'Эскалация...' : 'Эскалировать'}
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {showRaci && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-[60] p-4" onClick={() => setShowRaci(false)}>
          <div onClick={e => e.stopPropagation()}>
            <RACIGrid taskId={taskId} onClose={() => { setShowRaci(false); fetchTask(); }} />
          </div>
        </div>
      )}
    </div>
  );
}

export default TaskDetailModal;