import fs from 'node:fs';
import path from 'node:path';
import yaml from 'js-yaml';

const dataDir = path.join(process.cwd(), 'src', 'data');

export interface MenuLink {
  name: string;
  description: string;
  href: string;
}

export interface SiteInfo {
  name: string;
  tagline: string;
  address: string;
  phone: string;
  hours: { weekday: string; closed: string };
  instagram: string;
  menuLinks: MenuLink[];
  kakaoMap: {
    key: string;
    timestamp: string;
    width: number;
    height: number;
    directionsUrl: string;
  };
}

/** 한 메뉴 안에 여러 사이즈/옵션이 있을 때 (예: 라떼 5부/8부, 휘낭시에 플레인/초코) */
export interface Variant {
  label: string;
  price: number;
}

export interface MenuItem {
  name: string;
  price?: number;          // 단일 가격 (variants 사용 시 생략 가능)
  variants?: Variant[];    // 사이즈·옵션·맛 등 다중 변형
  description?: string;
  image?: string;
  onlyHot?: boolean;   // 명시적으로 핫 전용임을 표시 (예: 마로치노)
  onlyIced?: boolean;  // 명시적으로 아이스 전용임을 표시
}

/** 카테고리 안의 서브섹션 헤더 (메뉴 항목이 아님). YAML에서 `- heading: ...` 로 표기. */
export interface MenuHeading {
  heading: string;
}

export type MenuEntry = MenuItem | MenuHeading;

export function isHeading(e: MenuEntry): e is MenuHeading {
  return (e as MenuHeading).heading !== undefined;
}

export interface MenuCategory {
  name: string;
  note?: string;       // 카테고리 헤더 아래 작은 안내 (예: "아이스 +500원")
  items: MenuEntry[];
}

export interface Menu {
  categories: MenuCategory[];
}

/** 공지/이벤트 팝업 버튼 (선택) */
export interface NoticeButton {
  label: string;
  url: string;
}

/** 홈 진입 시 뜨는 공지/이벤트 팝업 설정 — src/data/notice.yaml */
export interface Notice {
  enabled: boolean;
  version?: number;
  image?: string;
  imageAlt?: string;
  title?: string;
  body?: string;
  button?: NoticeButton | null;
}

function load<T>(filename: string): T {
  const content = fs.readFileSync(path.join(dataDir, filename), 'utf8');
  return yaml.load(content) as T;
}

export const info: SiteInfo = load<SiteInfo>('info.yaml');
export const menu: Menu = load<Menu>('menu.yaml');
export const notice: Notice = load<Notice>('notice.yaml');
