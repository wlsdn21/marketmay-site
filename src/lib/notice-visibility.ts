// 브라우저에서도 안전한 순수 로직 (node 모듈 import 금지 — 이 파일은 클라이언트 번들에 포함됨)

/** Date를 로컬 기준 YYYY-MM-DD 문자열로 변환. */
export function dateKey(d: Date): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

/** '오늘 하루 보지 않기' 저장 포맷: "{version}:{YYYY-MM-DD}" */
export function dismissValue(version: number, today: string): string {
  return `${version}:${today}`;
}

/**
 * 지금 팝업을 보여줘야 하는가?
 * 같은 version을 같은 날짜에 '오늘 하루 보지 않기'로 닫은 경우에만 false.
 * 그 외(저장값 없음 / 날짜 지남 / version 변경 / 형식 깨짐)는 모두 true.
 */
export function shouldShowNotice(stored: string | null, version: number, today: string): boolean {
  if (!stored) return true;
  const idx = stored.indexOf(':');
  if (idx === -1) return true;
  const storedVersion = stored.slice(0, idx);
  const storedDate = stored.slice(idx + 1);
  if (storedVersion !== String(version)) return true;
  if (storedDate !== today) return true;
  return false;
}
