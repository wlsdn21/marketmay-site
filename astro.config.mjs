// @ts-check
import { defineConfig } from 'astro/config';

// https://astro.build/config
export default defineConfig({
  redirects: {
    '/menu/ja': '/menu/en/',
    '/menu/zh': '/menu/en/',
  },
});
