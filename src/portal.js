const portalForm = document.querySelector("#portal-search-form");
const portalSearchInput = document.querySelector("#portal-search-input");
const showResultsButton = document.querySelector("#show-results-button");

function goToSearch(query = "") {
  const trimmedQuery = query.trim();
  const destination = trimmedQuery
    ? `./search.html?q=${encodeURIComponent(trimmedQuery)}`
    : "./search.html";

  window.location.href = destination;
}

portalForm?.addEventListener("submit", (event) => {
  event.preventDefault();
  goToSearch(portalSearchInput?.value ?? "");
});

showResultsButton?.addEventListener("click", () => {
  goToSearch();
});
