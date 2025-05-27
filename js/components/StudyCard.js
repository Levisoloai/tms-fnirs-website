export function StudyCard({ title, journal, year, summary, doi }) {
  const card = document.createElement("div");
  card.className = "card study"; // Added 'study' class for potential specific styling
  card.innerHTML = `<h4>${title}</h4>
<p><em>${journal || "Journal information not available"}, ${year || "Year not available"}</em></p>
<p>${summary || "Summary not available."}</p>
<a href='https://doi.org/${doi}' target='_blank' aria-label='Read more about ${title} on DOI.org' class='doi-link'>Read More (DOI) <i class='fas fa-external-link-alt'></i></a>`; // Enhanced link

  // Add basic styling for the card directly in the component for encapsulation if desired,
  // or rely on existing CSS. For now, relying on existing .card styles and potential .study styles.
  // Example of adding direct styles (optional, and generally better in CSS files):
  // card.style.border = "1px solid #eee";
  // card.style.padding = "15px";
  // card.style.marginBottom = "15px";
  // card.style.borderRadius = "5px";

  return card;
}
