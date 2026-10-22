import type { ReactNode, SVGProps } from "react";

export type IconName = "home" | "book" | "search" | "chart" | "chat" | "settings" | "document" | "clock" | "users" | "check" | "bell" | "chevron" | "tag" | "shield" | "send" | "help";

const paths: Record<IconName, ReactNode> = {
  home: <><path d="M3 10.75 12 3l9 7.75" /><path d="M5.5 9.5V21h13V9.5M9.25 21v-6.75h5.5V21" /></>,
  book: <><path d="M4 4.5c2.8-.8 5.47-.2 8 1.8v14c-2.53-2-5.2-2.6-8-1.8z" /><path d="M20 4.5c-2.8-.8-5.47-.2-8 1.8v14c2.53-2 5.2-2.6 8-1.8z" /></>,
  search: <><circle cx="10.5" cy="10.5" r="6.5" /><path d="m15.5 15.5 5 5" /></>,
  chart: <><path d="M5 20V11M12 20V4M19 20v-7" /><path d="M3 20.5h18" /></>,
  chat: <path d="M4 5.5h16v11H9l-5 3z" />,
  settings: <><circle cx="12" cy="12" r="3" /><path d="M19.4 15a1.7 1.7 0 0 0 .34 1.88l.06.06-2.86 2.86-.06-.06A1.7 1.7 0 0 0 15 19.4a1.7 1.7 0 0 0-1 .6 1.7 1.7 0 0 0-.4 1.1V21h-4v-.1A1.7 1.7 0 0 0 8.6 19.4a1.7 1.7 0 0 0-1.88.34l-.06.06-2.86-2.86.06-.06A1.7 1.7 0 0 0 4.2 15a1.7 1.7 0 0 0-.6-1 1.7 1.7 0 0 0-1.1-.4H2.4v-4h.1A1.7 1.7 0 0 0 4.2 8.6a1.7 1.7 0 0 0-.34-1.88l-.06-.06L6.66 3.8l.06.06A1.7 1.7 0 0 0 8.6 4.2a1.7 1.7 0 0 0 1-.6 1.7 1.7 0 0 0 .4-1.1v-.1h4v.1a1.7 1.7 0 0 0 1 1.7 1.7 1.7 0 0 0 1.88-.34l.06-.06 2.86 2.86-.06.06A1.7 1.7 0 0 0 19.4 8.6a1.7 1.7 0 0 0 .6 1 1.7 1.7 0 0 0 1.1.4h.1v4h-.1a1.7 1.7 0 0 0-1.7 1Z" /></>,
  document: <><path d="M6 2.75h8l4 4V21.25H6z" /><path d="M14 2.75v4h4M9 12h6M9 16h6" /></>,
  clock: <><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3.5 2" /></>,
  users: <><circle cx="9" cy="8" r="3" /><circle cx="17" cy="9" r="2.5" /><path d="M3.5 20v-2.25A4.75 4.75 0 0 1 8.25 13h1.5a4.75 4.75 0 0 1 4.75 4.75V20M14.5 14.25a4 4 0 0 1 6 3.45V20" /></>,
  check: <path d="m4 12.5 5 5L20 6.5" />,
  bell: <><path d="M6.5 9.5a5.5 5.5 0 0 1 11 0c0 6 2.5 6.5 2.5 6.5H4s2.5-.5 2.5-6.5Z" /><path d="M9.75 19a2.4 2.4 0 0 0 4.5 0" /></>,
  chevron: <path d="m8 10 4 4 4-4" />,
  tag: <><path d="M3.5 11.5V4h7.5L21 14l-7 7z" /><circle cx="7.75" cy="8.25" r="1" /></>,
  shield: <><path d="M12 2.75 20 6v5.5c0 5-3.4 8.25-8 10-4.6-1.75-8-5-8-10V6z" /><path d="m8.5 12 2.25 2.25L15.5 9.5" /></>,
  send: <><path d="m3 4 18 8-18 8 3-8z" /><path d="M6 12h15" /></>,
  help: <><circle cx="12" cy="12" r="9" /><path d="M9.6 9.4a2.5 2.5 0 1 1 3.5 2.3c-.7.3-1.1.9-1.1 1.6v.4" /><path d="M12 17h.01" /></>,
};

export function UiIcon({ name, ...props }: { name: IconName } & SVGProps<SVGSVGElement>) {
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>{paths[name]}</svg>;
}
