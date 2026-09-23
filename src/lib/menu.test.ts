import { describe, expect, it } from 'vitest';
import drinks from '../data/drinks.json';
import brunch from '../data/brunch.json';
import { getMenu, languages } from './menu';
const available = [
  ...brunch.items,
  ...['coffee', 'drinks', 'fruit', 'tea'].flatMap(id => drinks.sections.find(section => section.id === id)!.items),
];
describe('multilingual QR menu', () => {
  for (const language of languages) {
    it(language.code + ': translates the full menu while preserving prices and conditions', () => {
      const menu = getMenu(language.code);
      expect(menu.sections.map(section => section.id)).toEqual(['brunch', 'coffee', 'drinks', 'fruit', 'tea']);
      const items = menu.sections.flatMap(section => section.items);
      expect(items.map(item => [item.id, item.price])).toEqual(available.map(item => [item.id, item.price]));
      expect(items).toHaveLength(42);
      expect(menu.sections.some(section => section.id === 'seasonal')).toBe(false);
      expect(items.filter(item => item.hotOnly)).toHaveLength(3);
      const brunchSection = menu.sections.find(section => section.id === 'brunch')!;
      expect(brunchSection.items).toHaveLength(11);
      expect(brunchSection.note).toMatch(language.code === 'ko' ? /3시/ : /3 PM/);
      expect(brunchSection.items.filter(item => item.isNew).map(item => [item.id, item.price])).toEqual([
        ['chili-egg', 14000], ['fig-jambon', 14000],
      ]);
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
        expect(menu.formatPrice(5000)).toBe('₩5,000');
      }
    });
  }
});
