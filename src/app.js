const searchableFields = [
  "title",
  "translation",
  "artist",
  "artistKr",
  "language",
  "genre",
  "theme",
  "songIntro",
  "sourceNote",
  "workTitle",
  "tags"
];

const state = {
  songs: [],
  query: "",
  filters: {
    language: new Set(),
    genre: new Set(),
    mood: new Set()
  },
  pickFirst: false,
  sortKey: "default",
  hasUserInteracted: false
};

const searchInput = document.querySelector("#search-input");
const stickySearchInput = document.querySelector("#sticky-search-input");
const hero = document.querySelector(".hero");
const resultSummary = document.querySelector("#result-summary");
const stickyResultSummary = document.querySelector("#sticky-result-summary");
const songList = document.querySelector("#song-list");
const randomAllButton = document.querySelector("#random-all-button");
const randomVisibleButton = document.querySelector("#random-visible-button");
const randomResult = document.querySelector("#random-result");
const filterOptionContainers = {
  language: document.querySelector("#language-filter-options"),
  genre: document.querySelector("#genre-filter-options"),
  mood: document.querySelector("#mood-filter-options")
};
const filterMenus = document.querySelectorAll(".filter-menu");
const pickFirstToggle = document.querySelector("#pick-first-toggle");
const sortSelect = document.querySelector("#sort-select");
const searchButton = document.querySelector(".search-button");
const isSearchPage = Boolean(
  searchInput &&
  stickySearchInput &&
  resultSummary &&
  stickyResultSummary &&
  songList &&
  randomAllButton &&
  randomVisibleButton &&
  randomResult &&
  pickFirstToggle &&
  sortSelect
);

function normalizeText(value) {
  return String(value ?? "")
    .toLowerCase()
    .normalize("NFKC")
    .trim();
}

function matchesSearch(song, query) {
  const terms = normalizeText(query).split(/\s+/).filter(Boolean);
  if (terms.length === 0) return true;

  const fields = searchableFields.map((field) => normalizeText(song[field]));

  return terms.every((term) =>
    fields.some((fieldValue) => fieldValue.includes(term))
  );
}

function matchesSetFilter(value, selectedValues) {
  if (selectedValues.size === 0) return true;
  return selectedValues.has(value);
}

function matchesGenreFilter(song) {
  const selectedValues = state.filters.genre;
  if (selectedValues.size === 0) return true;
  return [song.genre1, song.genre2].some((genre) => selectedValues.has(genre));
}

function matchesFilters(song) {
  return (
    matchesSetFilter(song.language, state.filters.language) &&
    matchesGenreFilter(song) &&
    matchesSetFilter(song.emotion, state.filters.mood)
  );
}

function getOriginalOrder(song) {
  return state.songs.indexOf(song);
}

function compareText(first, second) {
  return normalizeText(first).localeCompare(normalizeText(second), "ko");
}

function compareSelectedSort(first, second) {
  if (state.sortKey === "title") {
    return compareText(first.title, second.title);
  }

  if (state.sortKey === "artist") {
    return compareText(first.artist, second.artist) || compareText(first.title, second.title);
  }

  if (state.sortKey === "singCount") {
    return Number(second.singCount || 0) - Number(first.singCount || 0);
  }

  return 0;
}

function compareSongs(first, second) {
  if (state.pickFirst && first.pick !== second.pick) {
    return first.pick ? -1 : 1;
  }

  return compareSelectedSort(first, second) || getOriginalOrder(first) - getOriginalOrder(second);
}

function hasActiveSearchState() {
  return (
    state.query.trim() ||
    state.filters.language.size ||
    state.filters.genre.size ||
    state.filters.mood.size
  );
}

function getVisibleSongs() {
  const visibleSongs = state.songs.filter(
    (song) => matchesSearch(song, state.query) && matchesFilters(song)
  );

  return [...visibleSongs].sort(compareSongs);
}

function getRandomSong(songs) {
  if (songs.length === 0) return null;
  return songs[Math.floor(Math.random() * songs.length)];
}

function getYouTubeVideoId(url) {
  if (!url) return "";

  try {
    const parsedUrl = new URL(url);
    if (parsedUrl.hostname.includes("youtu.be")) {
      return parsedUrl.pathname.split("/").filter(Boolean)[0] || "";
    }

    return parsedUrl.searchParams.get("v") || "";
  } catch {
    return "";
  }
}

function getThumbnailUrl(song) {
  if (song.thumbnailUrl) return song.thumbnailUrl;
  const videoId = getYouTubeVideoId(song.videoUrl);
  return videoId ? `https://img.youtube.com/vi/${videoId}/mqdefault.jpg` : "";
}

function createLinkButton(url, label) {
  if (!url) {
    return `<span class="button button-disabled" aria-disabled="true">📄 가사 준비 중</span>`;
  }

  return `<a class="button" href="${url}" target="_blank" rel="noopener noreferrer">${label}</a>`;
}

function getArtistLine(song) {
  const artistMeta = [song.artistKr, song.language].filter(Boolean).join(" · ");
  return `${song.artist}${artistMeta ? ` · ${artistMeta}` : ""}`;
}

function getTranslatedTitle(song, className) {
  if (!song.translation || normalizeText(song.translation) === normalizeText(song.title)) {
    return "";
  }

  return `<p class="${className}">${song.translation}</p>`;
}

function getSongChips(song) {
  return [song.language, song.genre1, song.emotion || song.sourceType]
    .map((chip) => String(chip ?? "").trim())
    .filter(Boolean)
    .filter((chip, index, chips) => chips.indexOf(chip) === index)
    .slice(0, 3);
}

function getCompactMetaLine(song) {
  return [song.genre1, song.genre2 || song.sourceType, song.sourceNote]
    .map((item) => String(item ?? "").trim())
    .filter(Boolean)
    .filter((item, index, items) => items.indexOf(item) === index)
    .join(" · ");
}

function renderRandomSong(song) {
  if (!song) {
    randomResult.innerHTML = `<p>현재 검색 결과에 추천할 곡이 없습니다.</p>`;
    return;
  }

  const thumbnailUrl = getThumbnailUrl(song);
  const thumbnail = thumbnailUrl
    ? `<img src="${thumbnailUrl}" alt="" loading="lazy">`
    : `<span>♪</span>`;
  const thumbContent = `
    <div class="random-thumb" aria-hidden="true">
      ${thumbnail}
    </div>
  `;
  const thumb = song.videoUrl
    ? `<a class="random-thumb-link" href="${song.videoUrl}" target="_blank" rel="noopener noreferrer" aria-label="${song.title} 영상 열기">${thumbContent}</a>`
    : thumbContent;
  const translatedTitle = getTranslatedTitle(song, "random-translation");
  const songIntro = song.songIntro
    ? `<p class="random-intro">${song.songIntro}</p>`
    : "";
  const chips = getSongChips(song);
  const chipList = chips.length
    ? `<div class="random-chip-list">${chips.map((chip) => `<span class="song-chip">${chip}</span>`).join("")}</div>`
    : "";
  const lyricsButton = createLinkButton(song.lyricsUrl, "📄 가사");

  randomResult.innerHTML = `
    <article class="random-song">
      ${thumb}
      <div class="random-song-body">
        <h3>${song.title}</h3>
        ${translatedTitle}
        <p class="random-artist">${getArtistLine(song)}</p>
        ${songIntro}
        ${chipList}
        <div class="random-link-row">
          ${lyricsButton}
        </div>
      </div>
    </article>
  `;
}

function updateRandomButtons() {
  randomAllButton.disabled = state.songs.length === 0;
  randomVisibleButton.disabled = getVisibleSongs().length === 0;
}

function renderSongCard(song) {
  const pickBadge = song.pick ? `<span class="pick-badge">🍵 Pick</span>` : "";
  const thumbnailUrl = getThumbnailUrl(song);
  const thumbnail = thumbnailUrl
    ? `<img src="${thumbnailUrl}" alt="" loading="lazy">`
    : `<span>♪</span>`;
  const translatedTitle = getTranslatedTitle(song, "song-translation");
  const themeText = getCompactMetaLine(song);
  const chips = getSongChips(song);
  const songIntro = song.songIntro
    ? `<p class="song-intro">${song.songIntro}</p>`
    : "";
  const singCount = Number.isFinite(Number(song.singCount))
    ? `<span class="song-count">🎙 ${Number(song.singCount)}회</span>`
    : "";
  const lyricsButton = createLinkButton(song.lyricsUrl, "📄 가사");
  const thumbContent = `
    <div class="song-thumb" aria-hidden="true">
      ${thumbnail}
    </div>
  `;
  const thumb = song.videoUrl
    ? `<a class="song-thumb-link" href="${song.videoUrl}" target="_blank" rel="noopener noreferrer" aria-label="${song.title} 영상 열기">${thumbContent}</a>`
    : thumbContent;

  return `
    <article class="song-card">
      ${thumb}
      <div class="song-main">
        <div class="song-title-block">
          <div class="song-card-header">
            <h3>${song.title}</h3>
            ${pickBadge}
          </div>
          ${translatedTitle}
          <p class="song-artist">${getArtistLine(song)}</p>
          ${songIntro}
        </div>

        <div class="song-meta">
          <p class="song-theme">${themeText}</p>
          <div class="song-chip-list">
            ${chips.map((chip) => `<span class="song-chip">${chip}</span>`).join("")}
          </div>
        </div>

        <div class="song-actions">
          ${lyricsButton}
          ${singCount}
        </div>
      </div>
    </article>
  `;
}

function render() {
  const visibleSongs = getVisibleSongs();
  updateRandomButtons();
  updatePageMode();

  const summaryText = hasActiveSearchState()
    ? `${visibleSongs.length}곡`
    : `전체 ${visibleSongs.length}곡`;
  resultSummary.textContent = summaryText;
  stickyResultSummary.textContent = summaryText;

  if (visibleSongs.length === 0) {
    songList.innerHTML = `<p class="empty-message">조건에 맞는 곡이 없습니다.</p>`;
    return;
  }

  songList.innerHTML = visibleSongs.map(renderSongCard).join("");
}

function setPortalMode() {
  document.body.classList.remove("portal-mode");
  document.body.classList.add("results-mode");
}

function setResultsMode() {
  state.hasUserInteracted = true;
  document.body.classList.add("results-mode", "has-active-search");
  document.body.classList.remove("portal-mode");
}

function updatePageMode() {
  setResultsMode();
}

function getUniqueValues(extractor) {
  return [
    ...new Set(
      state.songs
        .flatMap(extractor)
        .map((value) => String(value ?? "").trim())
        .filter(Boolean)
    )
  ].sort((first, second) => first.localeCompare(second, "ko"));
}

function renderFilterOptions(filterName, values) {
  filterOptionContainers[filterName].innerHTML = values
    .map(
      (value) => `
        <label class="filter-option">
          <input type="checkbox" value="${value}" data-filter="${filterName}">
          <span>${value}</span>
        </label>
      `
    )
    .join("");
}

function renderFilters() {
  renderFilterOptions("language", getUniqueValues((song) => [song.language]));
  renderFilterOptions("genre", getUniqueValues((song) => [song.genre1, song.genre2]));
  renderFilterOptions("mood", getUniqueValues((song) => [song.emotion]));
}

function updateFilterSummary(filterName) {
  const menu = document.querySelector(`.filter-menu[data-filter="${filterName}"]`);
  const summary = menu.querySelector("summary");
  const selectedCount = state.filters[filterName].size;
  summary.dataset.count = selectedCount ? String(selectedCount) : "";
}

async function loadSongs() {
  try {
    const response = await fetch("./data/songs.json");
    if (!response.ok) {
      throw new Error(`songs.json load failed: ${response.status}`);
    }

    state.songs = await response.json();
    renderFilters();
    applyInitialQuery();
    render();
    maybeRenderInitialRandom();
  } catch (error) {
    console.error(error);
    resultSummary.textContent = "곡 데이터를 불러오지 못했습니다.";
    songList.innerHTML = `
      <p class="empty-message">
        로컬 서버로 실행했는지 확인해주세요.
      </p>
    `;
  }
}

function applyInitialQuery() {
  const params = new URLSearchParams(window.location.search);
  const query = params.get("q") || "";

  if (!query) return;

  state.query = query;
  state.hasUserInteracted = true;
  searchInput.value = query;
  stickySearchInput.value = query;
}

function maybeRenderInitialRandom() {
  const params = new URLSearchParams(window.location.search);
  if (params.get("random") === "1") {
    renderRandomSong(getRandomSong(state.songs));
  }
}

function updateQuery(value, sourceInput) {
  state.query = value;
  if (value.trim()) setResultsMode();
  if (sourceInput !== searchInput) searchInput.value = value;
  if (sourceInput !== stickySearchInput) stickySearchInput.value = value;
  render();
}

if (isSearchPage) {
  searchInput.addEventListener("input", (event) => {
    updateQuery(event.target.value, searchInput);
  });

  if (searchButton) {
    searchButton.addEventListener("click", () => {
      setResultsMode();
      render();
    });
  }

  stickySearchInput.addEventListener("input", (event) => {
    updateQuery(event.target.value, stickySearchInput);
  });

  if (hero && typeof window !== "undefined") {
    function updateStickySearchVisibility() {
      const revealPoint = hero.offsetTop + hero.offsetHeight - 80;
      document.body.classList.toggle("sticky-search-visible", window.scrollY > revealPoint);
    }

    window.addEventListener("scroll", updateStickySearchVisibility, { passive: true });
    window.addEventListener("resize", updateStickySearchVisibility);
    updateStickySearchVisibility();
  }

  Object.values(filterOptionContainers).forEach((container) => {
    container.addEventListener("change", (event) => {
      const checkbox = event.target;
      const filterName = checkbox.dataset.filter;
      const selectedValues = state.filters[filterName];

      if (checkbox.checked) {
        selectedValues.add(checkbox.value);
      } else {
        selectedValues.delete(checkbox.value);
      }

      setResultsMode();
      updateFilterSummary(filterName);
      render();
    });
  });

  filterMenus.forEach((menu) => {
    menu.addEventListener("toggle", () => {
      if (!menu.open) return;
      filterMenus.forEach((otherMenu) => {
        if (otherMenu !== menu) otherMenu.open = false;
      });
    });
  });

  pickFirstToggle.addEventListener("click", () => {
    setResultsMode();
    state.pickFirst = !state.pickFirst;
    pickFirstToggle.setAttribute("aria-pressed", String(state.pickFirst));
    pickFirstToggle.classList.toggle("chip-active", state.pickFirst);
    render();
  });

  sortSelect.addEventListener("change", (event) => {
    setResultsMode();
    state.sortKey = event.target.value;
    render();
  });

  randomAllButton.addEventListener("click", () => {
    renderRandomSong(getRandomSong(state.songs));
  });

  randomVisibleButton.addEventListener("click", () => {
    setResultsMode();
    renderRandomSong(getRandomSong(getVisibleSongs()));
  });

  loadSongs();
}
