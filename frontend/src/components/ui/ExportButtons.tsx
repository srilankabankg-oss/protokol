interface Props {
  meetingId: string;
}

function ExportButtons({ meetingId }: Props) {
  const pdfUrl = `/api/v1/meetings/${meetingId}/export/pdf`;
  const xlsxUrl = `/api/v1/meetings/${meetingId}/export/xlsx`;

  return (
    <div className="flex gap-2">
      <a
        href={pdfUrl}
        target="_blank"
        rel="noopener noreferrer"
        className="px-3 py-1.5 text-xs bg-red-600 text-white rounded hover:bg-red-700 font-medium"
      >
        📄 PDF
      </a>
      <a
        href={xlsxUrl}
        target="_blank"
        rel="noopener noreferrer"
        className="px-3 py-1.5 text-xs bg-green-600 text-white rounded hover:bg-green-700 font-medium"
      >
        📊 Excel
      </a>
    </div>
  );
}

export default ExportButtons;