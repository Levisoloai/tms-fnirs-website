# TMS‑fNIRS Technology Microsite

An open‑source educational microsite that explains and showcases the integration of **Transcranial Magnetic Stimulation (TMS)** with **Functional Near‑Infrared Spectroscopy (fNIRS)** for research and clinical applications.

## ✨  Features

* **Data‑driven content** – Study cards, market stats and reference list are generated from JSON / BibTeX sources.
* **Modern toolchain** – Prettier, ESLint, CSpell, and automated reference builder.
* **Accessible & responsive** – WCAG 2.2 AA colour contrast, keyboard‑navigable, print‑friendly.
* **No build step required** – Pure HTML + Vanilla JS served by `lite-server` for local dev.

## 🗂  Project structure

```
├── index.html              # Main page (placeholder tags consumed at build)
├── css/
│   └── styles.css          # Global styles
├── images/                 # Static assets
├── js/
│   ├── main.js             # App bootstrap
│   └── components/
│       ├── StudyCard.js    # Reusable study card component
│       └── MarketStat.js   # Inline SVG sparkline component
├── data/
│   ├── studies.json        # Curated 2023‑2025 literature summaries
│   └── market.json         # Market CAGR / TAM figures
├── research_sources/
│   └── lit_tms_fnirs_2025.bib  # Full BibTeX library
├── scripts/
│   └── buildReferences.js  # Generates partials/references.html
├── partials/
│   └── references.html     # Auto‑generated APA‑7 reference list
└── package.json            # Dev toolchain & scripts
```

## 🚀  Getting started

### Prerequisites

* **Node.js >= 18**

```bash
# Clone repository and install dev dependencies
npm install

# Start local dev server (auto‑reload)
npm run dev
```

### Building references and other assets

```bash
# Parse BibTeX and inject formatted APA‑7 list into index.html
npm run build:refs
```

### QA & formatting

```bash
npm run prettier   # auto‑format code & markup
npm run lint       # ESLint (StandardJS rules)
npm run spell      # Spell‑check documentation & HTML
```

All three must pass with **0 errors** before opening a pull request.

## 🤝  Contributing

1. Fork the repo and create a feature branch.
2. Follow the same QA steps (`prettier`, `lint`, `spell`).
3. Submit a PR with a concise description and link to Issue (if applicable).

## 📄  License

[MIT](LICENSE) – see LICENSE file for details.
