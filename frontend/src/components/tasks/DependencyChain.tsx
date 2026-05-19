import { useState, useEffect } from 'react';
import { getDependencies, getRaci } from '../../api/client';

interface Props {
  taskId: string;
}

function DependencyChain({ taskId }: Props) {
  const [chain, setChain] = useState<{ id: string; label: string }[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchChain();
  }, [taskId]);

  async function fetchChain() {
    setLoading(true);
    try {
      const collected: { id: string; label: string }[] = [];
      let current: string | undefined = taskId;

      for (let i = 0; i < 10 && current; i++) {
        const depData = await getDependencies(current);
        const prevId = depData.graph_edges?.previous_task_id;

        if (prevId) {
          try {
            const raciData = await getRaci(prevId);
            collected.unshift({
              id: prevId,
              label: raciData.task_id.slice(0, 8),
            });
          } catch {
            collected.unshift({ id: prevId, label: prevId.slice(0, 8) });
          }
          current = prevId;
        } else {
          collected.unshift({ id: current, label: '●' });
          break;
        }
      }

      current = taskId;
      for (let i = 0; i < 10 && current; i++) {
        const depData = await getDependencies(current);
        const nextId = depData.graph_edges?.next_task_id;

        if (nextId && nextId !== taskId) {
          collected.push({ id: nextId, label: nextId.slice(0, 8) });
          current = nextId;
        } else {
          break;
        }
      }

      if (collected.length === 0) {
        collected.push({ id: taskId, label: '●' });
      }
      setChain(collected);
    } catch {
      setChain([{ id: taskId, label: '●' }]);
    } finally {
      setLoading(false);
    }
  }

  if (loading) return <div className="text-xs text-gray-400">Загрузка цепочки...</div>;
  if (chain.length === 0) return <div className="text-xs text-gray-400">Нет связанных задач</div>;

  return (
    <div className="overflow-x-auto py-2">
      <div className="flex items-center gap-1 min-w-max">
        {chain.map((node, i) => (
          <div key={node.id} className="flex items-center gap-1">
            <div className={`px-2 py-1 rounded text-xs font-mono whitespace-nowrap ${
              node.id === taskId
                ? 'bg-blue-100 text-blue-800 ring-2 ring-blue-300'
                : 'bg-gray-100 text-gray-600'
            }`}>
              {node.label}
            </div>
            {i < chain.length - 1 && (
              <span className="text-gray-300 text-xs">→</span>
            )}
          </div>
        ))}
      </div>
      <div className="text-xs text-gray-400 mt-1">
        Цепочка решений: {chain.length} задач(и)
      </div>
    </div>
  );
}

export default DependencyChain;