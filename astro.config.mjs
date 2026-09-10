// @ts-check
import { defineConfig } from 'astro/config';

// https://astro.build/config
export default defineConfig({
  server: {
    // Allow the workspace preview host during local development.
    allowedHosts: ['terminal.local'],
  },
});
