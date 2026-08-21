# Custom domain — pending

The documentation site is currently served from its Vercel URL:

**https://research-scan-docs.vercel.app** — live.

`docs.synectic.org` is the **planned** hostname. It is **not live**, not
configured, and not pointed anywhere. Nothing should link to it or cite it as an
address until the steps below are complete and verified.

## Steps to move to docs.synectic.org

### 1. Add the domain in Vercel

Vercel project **research-scan-docs**, team **Innovation Practice**:

*Project → Settings → Domains → Add* → `docs.synectic.org`

Vercel will show the DNS record it expects and will report the domain as
*Invalid Configuration* until that record resolves. That is normal.

### 2. Add the DNS record

At whichever DNS provider serves `synectic.org`, add the record Vercel asks for —
for a subdomain this is normally:

| Type | Name | Value |
|---|---|---|
| `CNAME` | `docs` | `cname.vercel-dns.com` |

Use the exact target Vercel displays rather than the one above if the two differ;
Vercel is authoritative for its own infrastructure.

Propagation is usually minutes. Vercel issues the TLS certificate automatically
once the record resolves.

### 3. Update the canonical origin

Canonical URLs and absolute OpenGraph URLs are derived from a single value.
Change it in **`astro.config.ts`**:

```diff
-  site: 'https://research-scan-docs.vercel.app',
+  site: 'https://docs.synectic.org',
```

Then regenerate the per-page metadata and rebuild:

```bash
python3 scripts/sync-page-meta.py
npm run build
```

`scripts/sync-page-meta.py` reads `site` from `astro.config.ts`, so this is the
only place the origin is written. Committing the regenerated pages updates the
canonical tag, `og:url` and `og:image` on all 24 pages at once.

There is a `TODO(domain)` marker on that line in `astro.config.ts`.

### 4. Decide what the old URL does

Vercel keeps serving `research-scan-docs.vercel.app` after a custom domain is
added. Once `docs.synectic.org` is live, set the custom domain as the project's
primary domain so the Vercel URL redirects to it, rather than leaving two
addresses serving identical content with the same canonical tag.

### 5. Verify

```bash
curl -sI https://docs.synectic.org/ | head -1
curl -s https://docs.synectic.org/ | grep -o '<link rel="canonical"[^>]*>'
curl -sI https://docs.synectic.org/reference/cli/ | head -1
```

Expect `200` on both pages and a canonical pointing at `docs.synectic.org`.

### 6. Update the main repo

The main repo's README links to the documentation site. Update that link in the
same change, so the two never disagree about where the docs live.
