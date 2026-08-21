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

## Domain

The site is live at **https://research-scan-docs.vercel.app**.

`docs.synectic.org` is planned but **not live** — see [`DOMAIN.md`](DOMAIN.md) for
the steps and the single place the origin is configured.

## License

Apache-2.0. See [`LICENSE`](LICENSE).
