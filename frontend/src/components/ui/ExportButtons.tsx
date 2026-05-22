interface Props {
  meetingId: string;
}

async function downloadWithAuth(url: string, filename: string) {
  const token = localStorage.getItem('access_token');
  const res = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok) throw new Error('Download failed');
  const blob = await res.blob();
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  a.click();
  URL.revokeObjectURL(a.href);
}

function ExportButtons({ meetingId }: Props) {
  return (
    <div className="flex gap-2">
      <button
        onClick={() => downloadWithAuth(`/api/v1/meetings/${meetingId}/export/pdf`, `protocol-${meetingId.slice(0,8)}.pdf`)}
        className="px-3 py-1.5 text-xs bg-red-600 text-white rounded hover:bg-red-700 font-medium"
      >
        📄 PDF
      </button>
      <button
        onClick={() => downloadWithAuth(`/api/v1/meetings/${meetingId}/export/xlsx`, `protocol-${meetingId.slice(0,8)}.xlsx`)}
        className="px-3 py-1.5 text-xs bg-green-600 text-white rounded hover:bg-green-700 font-medium"
      >
        📊 Excel
      </button>
    </div>
  );
}

export default ExportButtons;