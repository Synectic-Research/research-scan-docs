# research-scan-docs

Source for the [Research Scan](https://github.com/Synectic-Research/research-scan)
documentation site.

The product itself lives in the main repo. This repo holds only the site: Astro 7
with the [Lotus](https://astro-theme-lotus.prosefly.dev) documentation theme,
Tailwind CSS v4, and MDX. Static output, deployed on Vercel.

## Develop

```bash
npm install
npm run dev      # http://localhost:4321
npm run build    # static output in dist/
```

## Writing

Read [`DESIGN.md`](DESIGN.md) first. It carries the audience, the language rules
and the grounding rules this site is written against — in particular that the
main repo is the source of truth, and that every command shown must have a real
transcript behind it.

Content lives in `src/content/docs/**/*.mdx`. Navigation, site metadata and the
sidebar are configured in `theme.config.json`.

## Release pass

The current product release is declared in exactly one place:
`current_release` in [`scripts/release-facts.json`](scripts/release-facts.json).
**Every release pass updates it**, alongside the main repo's own
[`RELEASING.md`](https://github.com/Synectic-Research/research-scan/blob/main/RELEASING.md)
checklist. That same file carries the manifest of pages whose transcripts must
show the current release, and the allowlist of the older versions that stay
because they are release history or measurement provenance.

```bash
python3 scripts/check-versions.py
```

Bump `current_release` and this fails until every listed transcript is recaptured
against the new version. Recapture, never hand-edit: install the exact release
into a clean environment and paste the output verbatim. The check also holds the
narrower rules the site has been bitten by — the controlled-replay paragraph must
appear complete wherever its figures do, timing and cost figures live only on the
Measurements page, and the configuration pages must not describe `NCBI_API_KEY`
as enabling PubMed retrieval.

## Domain

The site is live at **https://researchscan.synectic.org**.

See [`DOMAIN.md`](DOMAIN.md) for the DNS record and the single place the origin
is configured.

## License

Apache-2.0. See [`LICENSE`](LICENSE).
