import type { MeetingStatus } from '../../types';

interface Props {
  currentStatus: MeetingStatus;
}

const STEPS: { status: MeetingStatus; label: string }[] = [
  { status: 'preparation', label: 'Подготовка' },
  { status: 'in_progress', label: 'Ведение' },
  { status: 'on_approval', label: 'Согласование' },
  { status: 'approved', label: 'Утверждено' },
];

function ApprovalStepper({ currentStatus }: Props) {
  const currentIdx = STEPS.findIndex(s => s.status === currentStatus);

  return (
    <div className="flex items-center gap-1 text-xs">
      {STEPS.map((step, i) => {
        const isCompleted = i < currentIdx;
        const isCurrent = i === currentIdx;

        return (
          <div key={step.status} className="flex items-center gap-1">
            <div className={`px-2 py-1 rounded-full whitespace-nowrap ${
              isCompleted ? 'bg-green-100 text-green-700' :
              isCurrent ? 'bg-blue-100 text-blue-700 font-medium' :
              'bg-gray-100 text-gray-400'
            }`}>
              {isCompleted ? '✓ ' : ''}{step.label}
            </div>
            {i < STEPS.length - 1 && (
              <span className={`w-4 h-px ${isCompleted ? 'bg-green-300' : 'bg-gray-200'}`} />
            )}
          </div>
        );
      })}
    </div>
  );
}

export default ApprovalStepper;