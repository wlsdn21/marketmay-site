import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import yaml from 'js-yaml';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const dataDir = path.join(__dirname, '..', 'data');

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
  kakaoMap: { embedSrc: string; directionsUrl: string };
}

export interface MenuItem {
  name: string;
  price: number;
  description?: string;
  image?: string;
}

export interface MenuCategory {
  name: string;
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
