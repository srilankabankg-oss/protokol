import { useEffect, useState, useCallback } from 'react';
import { getAIInsights, createTask } from '../../api/client';
import type { AIInsights } from '../../types';

interface Props {
  meetingId: string;
}

function AIPanel({ meetingId }: Props) {
  const [insights, setInsights] = useState<AIInsights | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [addingTask, setAddingTask] = useState<string | null>(null);

  const fetchInsights = useCallback(async () => {
    try {
      const data = await getAIInsights(meetingId);
      setInsights(data);
      setError(null);
    } catch {
      setError('AI недоступен');
    } finally {
      setLoading(false);
    }
  }, [meetingId]);

  useEffect(() => {
    fetchInsights();
    const timer = setInterval(fetchInsights, 10000);
    return () => clearInterval(timer);
  }, [fetchInsights]);

  async function handleAddTask(desc: string, tempId: string) {
    setAddingTask(tempId);
    try {
      await createTask({ meeting_id: meetingId, description: desc });
    } catch {
      alert('Ошибка при добавлении задачи');
    } finally {
      setAddingTask(null);
    }
  }

  const severityBorder: Record<string, string> = {
    CRITICAL: 'border-l-red-600 bg-red-50',
    HIGH: 'border-l-orange-500 bg-orange-50',
    MEDIUM: 'border-l-yellow-500 bg-yellow-50',
    LOW: 'border-l-gray-400 bg-gray-50',
  };

  return (
    <aside className="w-80 bg-white border-l p-4 overflow-y-auto shrink-0 hidden lg:block">
      <h3 className="font-semibold text-sm text-gray-700 mb-4">🤖 ИИ-Ассистент</h3>

      {loading && !insights && (
        <div className="space-y-3">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-16 bg-gray-100 rounded animate-pulse" />
          ))}
        </div>
      )}

      {error && <p className="text-sm text-red-500">{error}</p>}

      {insights && (
        <div className="space-y-6">
          <section>
            <h4 className="text-xs font-medium text-gray-500 uppercase mb-2">
              💡 Предложенные задачи ({insights.suggested_action_items.length})
            </h4>
            {insights.suggested_action_items.length === 0 && (
              <p className="text-xs text-gray-400">Нет предложений</p>
            )}
            <ul className="space-y-2">
              {insights.suggested_action_items.map(item => (
                <li key={item.temporary_id} className="bg-gray-50 rounded-lg p-3 text-sm">
                  <p className="text-gray-800">{item.extracted_description}</p>
                  <div className="flex items-center justify-between mt-2">
                    <span className="text-xs text-gray-400">
                      Уверенность: {(item.confidence_score * 100).toFixed(0)}%
                    </span>
                    <button
                      onClick={() => handleAddTask(item.extracted_description, item.temporary_id)}
                      disabled={addingTask === item.temporary_id}
                      className="text-xs px-2 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                    >
                      {addingTask === item.temporary_id ? '...' : '+ Добавить'}
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          </section>

          <section>
            <h4 className="text-xs font-medium text-gray-500 uppercase mb-2">
              ⚠️ Риски ({insights.detected_risks.length})
            </h4>
            {insights.detected_risks.length === 0 && (
              <p className="text-xs text-gray-400">Риски не обнаружены</p>
            )}
            <ul className="space-y-2">
              {insights.detected_risks.map(risk => (
                <li
                  key={risk.risk_id}
                  className={`border-l-4 rounded-r-lg p-3 text-sm ${severityBorder[risk.severity] || ''}`}
                >
                  <p className="font-medium text-gray-800">{risk.message}</p>
                  <p className="text-xs text-gray-500 mt-1 italic">«{risk.text_anchor}»</p>
                </li>
              ))}
            </ul>
          </section>

          <section>
            <h4 className="text-xs font-medium text-gray-500 uppercase mb-2">🎙 Live-транскрипт</h4>
            <div className="bg-gray-50 rounded-lg p-3 text-xs text-gray-400 h-24 overflow-y-auto">
              Транскрипт появится здесь...
            </div>
          </section>
        </div>
      )}
    </aside>
  );
}

export default AIPanel;