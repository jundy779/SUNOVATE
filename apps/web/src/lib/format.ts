const DATE = new Intl.DateTimeFormat("id-ID", { day: "2-digit", month: "short", year: "numeric" });
const DATE_TIME = new Intl.DateTimeFormat("id-ID", {
  day: "2-digit",
  month: "short",
  year: "numeric",
  hour: "2-digit",
  minute: "2-digit",
  timeZone: "Asia/Jakarta",
});

export function formatDate(value: string | null | undefined): string {
  if (!value) return "-";
  const date = new Date(value.length === 10 ? `${value}T00:00:00` : value);
  return Number.isNaN(date.getTime()) ? value : DATE.format(date);
}

export function formatDateTime(value: string | null | undefined): string {
  if (!value) return "-";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : `${DATE_TIME.format(date)} WIB`;
}
