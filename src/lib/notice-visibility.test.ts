import { describe, it, expect } from 'vitest';
import { shouldShowNotice, dismissValue, dateKey } from './notice-visibility';

describe('dateKey', () => {
  it('로컬 날짜를 YYYY-MM-DD(0 패딩)로 변환', () => {
    // month는 0-indexed: 5 = 6월
    expect(dateKey(new Date(2026, 5, 4))).toBe('2026-06-04');
    expect(dateKey(new Date(2026, 11, 9))).toBe('2026-12-09');
  });
});

describe('dismissValue', () => {
  it('version과 날짜를 "{version}:{date}"로 결합', () => {
    expect(dismissValue(1, '2026-06-04')).toBe('1:2026-06-04');
    expect(dismissValue(3, '2026-12-09')).toBe('3:2026-12-09');
  });
});

describe('shouldShowNotice', () => {
  it('저장값이 없으면 노출', () => {
    expect(shouldShowNotice(null, 1, '2026-06-04')).toBe(true);
    expect(shouldShowNotice('', 1, '2026-06-04')).toBe(true);
  });
  it('같은 version을 오늘 닫았으면 숨김', () => {
    expect(shouldShowNotice('1:2026-06-04', 1, '2026-06-04')).toBe(false);
  });
  it('날짜가 지나면 다시 노출', () => {
    expect(shouldShowNotice('1:2026-06-03', 1, '2026-06-04')).toBe(true);
  });
  it('version이 바뀌면(새 공지) 다시 노출', () => {
    expect(shouldShowNotice('1:2026-06-04', 2, '2026-06-04')).toBe(true);
  });
  it('저장값 형식이 깨졌으면 노출', () => {
    expect(shouldShowNotice('garbage', 1, '2026-06-04')).toBe(true);
  });
});
