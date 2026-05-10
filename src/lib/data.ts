import fs from 'node:fs';
import path from 'node:path';
import yaml from 'js-yaml';

const dataDir = path.join(process.cwd(), 'src', 'data');

export interface Floor {
  code: string;
  name: string;
  description: string;
}

export interface SiteInfo {
  name: string;
  tagline: string;
  address: string;
  phone: string;
  hours: { weekday: string; closed: string };
  instagram: string;
  floors: Floor[];
  kakaoMap: {
    key: string;
    timestamp: string;
    width: number;
    height: number;
    directionsUrl: string;
  };
}

export interface MenuItem {
  name: string;
  price: number;
  description?: string;
  image?: string;
}

export interface MenuCategory {
  name: string;
  note?: string;       // 카테고리 헤더 아래 작은 안내 (예: "아이스 +500원")
  items: MenuItem[];
}

export interface Menu {
  categories: MenuCategory[];
}

function load<T>(filename: string): T {
  const content = fs.readFileSync(path.join(dataDir, filename), 'utf8');
  return yaml.load(content) as T;
}

export const info: SiteInfo = load<SiteInfo>('info.yaml');
export const menu: Menu = load<Menu>('menu.yaml');
