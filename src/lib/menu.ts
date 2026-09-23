import drinks from '../data/drinks.json';
import brunch from '../data/brunch.json';
import translations from '../data/menu/translations.json';

export const languages = [
  { code: 'ko', tag: 'ko', label: '한국어', href: '/menu/' },
  { code: 'en', tag: 'en', label: 'English', href: '/menu/en/' },
] as const;
export type MenuLocale = typeof languages[number]['code'];
type Copy = { name: string; detail?: string };
type Translation = {
  title: string; description: string; menuHeading: string; menuTagline: string; languageLabel: string; navLabel: string;
  decaf: string; freeChange: string; free: string; brunchOrderNote: string; newLabel: string;
  optionsTitle: string; hotOnly: string;
  sections: Record<string, string[]>; items: Record<string, Copy>; options: Record<string, Copy>;
};
const koreanDetails: Record<string, string> = {
  marocchino: '다크초콜릿을 올린 카푸치노',
  'earl-grey': '시트러스 과육을 넣은 홍차',
  'royal-milk-tea': '로얄 블렌드 홍차 · 우유 · 꿀',
  'iced-milk-tea': '블렌딩 홍차 냉침',
  belgian: '우유에 녹인 벨지안 다크초콜릿',
};
const korean: Translation = {
  title: '마켓메이 메뉴', description: '마켓메이 커피, 음료와 브런치 메뉴 및 가격.',
  menuHeading: '메뉴',
  menuTagline: '브런치 · 커피 · 음료',
  languageLabel: '메뉴 언어', navLabel: '메뉴 종류 바로가기',
  decaf: '모든 커피 디카페인 변경', freeChange: '무료', free: '무료',
  optionsTitle: '커피 추가 옵션', hotOnly: 'HOT ONLY', brunchOrderNote: '브런치는 오후 3시까지 주문 가능합니다.', newLabel: '신메뉴',
  sections: { coffee: ['커피', '커피'], fruit: ['에이드 · 과일차', '에이드·차'], tea: ['티 · 밀크티', '티'], drinks: ['라떼 · 음료', '라떼·음료'], brunch: ['브런치', '브런치'] },
  items: {}, options: {},
};

// The printed menu keeps its own source; this removal applies to the QR menu.
const sectionOrder = ['brunch', 'coffee', 'drinks', 'fruit', 'tea'];
export const webSections = [
  ...drinks.sections
    .map(section => ({ ...section, items: section.items.filter(item => item.id !== 'passion-fruit') }))
    .filter(section => section.items.length > 0),
  brunch,
].sort((a, b) => {
  const order = (id: string) => {
    const index = sectionOrder.indexOf(id);
    return index === -1 ? sectionOrder.length : index;
  };
  return order(a.id) - order(b.id);
});

export function getMenu(locale: MenuLocale) {
  const copy: Translation = locale === 'ko' ? korean : translations[locale];
  const sections = webSections.map(section => {
    if (!copy.sections[section.id]) throw new Error('Missing category translation: ' + locale + ' ' + section.id);
    return {
      id: section.id, name: copy.sections[section.id][0], nav: copy.sections[section.id][1],
      note: section.id === 'brunch' ? copy.brunchOrderNote : undefined,
      items: section.items.map(item => {
        const translated: Copy = locale === 'ko' ? {
          name: item.name, detail: koreanDetails[item.id] ?? ('detail' in item ? item.detail : undefined),
        } : copy.items[item.id];
        if (!translated?.name || ('detail' in item && !translated.detail)) {
          throw new Error('Missing menu translation: ' + locale + ' ' + item.id);
        }
        return {
          id: item.id, price: item.price,
          hotOnly: 'hotOnly' in item && item.hotOnly,
          isNew: 'new' in item && item.new,
          ...translated,
        };
      }),
    };
  });
  const options = drinks.options.filter(option => option.name !== '디카페인 원두 변경').map(option => {
    const translated: Copy = locale === 'ko' ? option : copy.options[option.name];
    if (!translated?.name || (option.detail && !translated.detail)) {
      throw new Error('Missing option translation: ' + locale + ' ' + option.name);
    }
    return { ...translated, price: option.price, refill: option.name === '아메리카노 리필' };
  });
  const decafPrice = drinks.options.find(option => option.name === '디카페인 원두 변경')?.price;
  const formatPrice = (value: number) => locale === 'ko' ? value.toLocaleString('ko-KR') + '원' : '₩' + value.toLocaleString('en-US');
  return { copy, sections, options, decafPrice, formatPrice };
}
