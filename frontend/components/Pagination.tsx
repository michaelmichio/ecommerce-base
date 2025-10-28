interface Props {
  page: number;
  pages: number;
  onPageChange: (page: number) => void;
}

export default function Pagination({ page, pages, onPageChange }: Props) {
  if (pages <= 1) return null;
  return (
    <div className="flex justify-center mt-6 gap-2">
      <button
        disabled={page <= 1}
        onClick={() => onPageChange(page - 1)}
        className="px-3 py-1 rounded bg-gray-200 disabled:opacity-50"
      >
        Prev
      </button>
      <span className="px-3 py-1 font-medium">
        {page} / {pages}
      </span>
      <button
        disabled={page >= pages}
        onClick={() => onPageChange(page + 1)}
        className="px-3 py-1 rounded bg-gray-200 disabled:opacity-50"
      >
        Next
      </button>
    </div>
  );
}
