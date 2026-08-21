import { defineConfig } from 'astro/config';
import lotus from '@prosefly/astro-theme-lotus';

export default defineConfig({
  site: 'https://researchscan.synectic.org',
  output: 'static',
  integrations: [lotus()],
});
