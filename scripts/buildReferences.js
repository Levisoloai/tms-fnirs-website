import fs from 'node:fs';
import { createRequire } from 'node:module';

// Use createRequire to import the CommonJS bibtex-parse-js module
const require = createRequire(import.meta.url);
const bibtexParse = require('bibtex-parse-js');

const bibPath = 'research_sources/lit_tms_fnirs_2025.bib';
const partialsDir = 'partials';
const outputPath = `${partialsDir}/references.html`;

// Ensure partials directory exists
if (!fs.existsSync(partialsDir)) {
  fs.mkdirSync(partialsDir, { recursive: true });
}

try {
  const bib = fs.readFileSync(bibPath, 'utf8');
  
  // bibtex-parse-js is expected to be an object with a toJSON method
  const entries = bibtexParse.toJSON(bib);

  const ol = entries
    .map(e => {
      const a = e.entryTags;
      const author = a.AUTHOR || 'Author not available';
      const year = a.YEAR || 'Year not available';
      const title = a.TITLE || 'Title not available';
      const journal = a.JOURNAL || a.BOOKTITLE || 'Journal/Venue not available';
      const doi = a.DOI;

      let listItem = `<li>${author} (${year}). ${title}. <em>${journal}</em>.`;
      if (doi) {
        listItem += ` <a href="https://doi.org/${doi}" target="_blank">https://doi.org/${doi}</a>`;
      }
      listItem += `</li>`;
      return listItem;
    })
    .join('\n');

  fs.writeFileSync(outputPath, `<ol>\n${ol}\n</ol>`);
  console.log(`✓ ${outputPath} regenerated`);

} catch (error) {
  console.error(`Error processing ${bibPath} or writing ${outputPath}:`, error);
  fs.writeFileSync(outputPath, '<p>Error generating references. Please check BibTeX file and console log.</p>');
  process.exit(1);
}
