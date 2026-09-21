import { describe, expect, it } from 'vitest';
import drinks from '../data/drinks.json';
import { getMenu, languages } from './menu';
const available = drinks.sections.flatMap(section => section.items).filter(item => item.id !== 'passion-fruit');
describe('multilingual QR menu', () => {
  for (const language of languages) {
    it(language.code + ': translates the full menu while preserving prices and conditions', () => {
      const menu = getMenu(language.code);
      const items = menu.sections.flatMap(section => section.items);
      expect(items.map(item => [item.id, item.price])).toEqual(available.map(item => [item.id, item.price]));
      expect(items).toHaveLength(31);
      expect(menu.sections.some(section => section.id === 'seasonal')).toBe(false);
      expect(items.filter(item => item.hotOnly)).toHaveLength(3);
      for (const original of available) {
        const item = items.find(item => item.id === original.id)!;
        expect(item.name.trim()).not.toBe('');
        if ('detail' in original) expect(item.detail?.trim()).toBeTruthy();
        if (language.code !== 'ko') expect(item.name + (item.detail ?? '')).not.toMatch(/[가-힣]/);
      }
      for (const section of menu.sections) {
        expect(section.name).toBeTruthy();
        expect(section.nav).toBeTruthy();
      }
      expect(menu.decafPrice).toBe(0);
      expect(menu.options.map(option => option.price)).toEqual([1000, 1000, 2500]);
      expect(menu.options.find(option => option.refill)?.detail).toBeTruthy();
      if (language.code !== 'ko') {
        expect(menu.options.map(option => option.name + (option.detail ?? '')).join(' ')).not.toMatch(/[가-힣]/);
        expect(menu.copy.currency).toContain('KRW');
        expect(menu.formatPrice(5000)).toBe('₩5,000');
      }
    });
  }
});
