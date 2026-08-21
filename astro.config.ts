import { defineConfig } from 'astro/config';
import lotus from '@prosefly/astro-theme-lotus';

// TODO(domain): when docs.synectic.org is provisioned, change `site` to
// 'https://docs.synectic.org' and redeploy. Canonical URLs and every absolute
// OpenGraph URL are derived from this value. See DOMAIN.md.
export default defineConfig({
  site: 'https://research-scan-docs.vercel.app',
  output: 'static',
  integrations: [lotus()],
});
