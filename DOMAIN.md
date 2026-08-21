# Domain

The production hostname configured for this deployment is
**researchscan.synectic.org**.

## DNS

`researchscan` is a `CNAME` at the DNS provider serving `synectic.org`, pointing
at the target Vercel assigns to this project. Proxy status is **DNS-only** — the
record resolves straight to Vercel, which terminates TLS and issues the
certificate for the hostname.

The exact target value is whatever the Vercel project's *Settings → Domains*
pane displays; Vercel is authoritative for its own infrastructure, so that pane
is the place to read it rather than this file.

## The canonical origin

Canonical URLs and every absolute OpenGraph URL derive from a single value:
`site` in **`astro.config.ts`**.

```ts
site: 'https://researchscan.synectic.org',
```

`scripts/sync-page-meta.py` reads that value, so nothing else in the repo writes
the hostname. After changing it, regenerate the per-page metadata:

```bash
python3 scripts/sync-page-meta.py
```

That rewrites the generated block on all 24 pages — canonical, `og:url` and
`og:image` — in one pass. `scripts/check-site.py` fails the build if any page's
canonical, `og:url` or `og:image` disagrees with `site`, and CI reruns the sync
script and fails on a diff, so a stale block cannot reach production.

`public/robots.txt` is the one static file that repeats the hostname, in its
`Sitemap:` line. CI checks that line against `site`.

## The Vercel URL

`research-scan-docs.vercel.app` still resolves. `vercel.json` redirects it,
permanently (308), to the same path on `researchscan.synectic.org`, so the two
hostnames never serve identical content under one canonical tag. The redirect is
host-scoped: preview deployments have their own hostnames and are unaffected.

## The main repo

The main repo's README links to this documentation site. That link carries the
same hostname, so the two never disagree about where the docs live.

## Verify

```bash
curl -sI https://researchscan.synectic.org/ | head -1
curl -s  https://researchscan.synectic.org/ | grep -o '<link rel="canonical"[^>]*>'
```
