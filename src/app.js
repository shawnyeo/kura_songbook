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
  sortKey: "default"
};

const searchInput = document.querySelector("#search-input");
const resultSummary = document.querySelector("#result-summary");
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

function renderRandomSong(song) {
  if (!song) {
    randomResult.innerHTML = `<p>현재 검색 결과에 추천할 곡이 없습니다.</p>`;
    return;
  }

  const translatedTitle = song.translation
    ? `<p class="random-translation">${song.translation}</p>`
    : "";
  const songIntro = song.songIntro
    ? `<p class="random-intro">${song.songIntro}</p>`
    : "";
  const videoButton = song.videoUrl
    ? `<a class="button" href="${song.videoUrl}" target="_blank" rel="noopener noreferrer">▶ 영상</a>`
    : "";
  const lyricsButton = createLinkButton(song.lyricsUrl, "📄 가사");

  randomResult.innerHTML = `
    <article class="random-song">
      <h3>${song.title}</h3>
      ${translatedTitle}
      <p class="random-artist">${getArtistLine(song)}</p>
      ${songIntro}
      <div class="random-link-row">
        ${videoButton}
        ${lyricsButton}
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
  const thumbnail = song.thumbnailUrl
    ? `<img src="${song.thumbnailUrl}" alt="" loading="lazy">`
    : `<span>♪</span>`;
  const translatedTitle = song.translation
    ? `<p class="song-translation">${song.translation}</p>`
    : "";
  const themeText = [song.genre, song.theme].filter(Boolean).join(" · ");
  const chips = [song.language, song.genre1, song.emotion].filter(Boolean);
  const songIntro = song.songIntro
    ? `<p class="song-intro">${song.songIntro}</p>`
    : "";
  const sourceNote = song.sourceNote
    ? `<p class="song-note">${song.sourceNote}</p>`
    : "";
  const singCount = Number.isFinite(Number(song.singCount))
    ? `<span class="song-count">🎙 ${Number(song.singCount)}회</span>`
    : "";
  const videoButton = song.videoUrl
    ? `<a class="button" href="${song.videoUrl}" target="_blank" rel="noopener noreferrer">▶ 영상</a>`
    : "";
  const lyricsButton = createLinkButton(song.lyricsUrl, "📄 가사");

  return `
    <article class="song-card">
      <div class="song-thumb" aria-hidden="true">
        ${thumbnail}
      </div>
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
          ${sourceNote}
          <div class="song-chip-list">
            ${chips.map((chip) => `<span class="song-chip">${chip}</span>`).join("")}
          </div>
        </div>

        <div class="song-actions">
          ${videoButton}
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

  resultSummary.textContent = hasActiveSearchState()
    ? `${visibleSongs.length}곡`
    : `전체 ${visibleSongs.length}곡`;

  if (visibleSongs.length === 0) {
    songList.innerHTML = `<p class="empty-message">조건에 맞는 곡이 없습니다.</p>`;
    return;
  }

  songList.innerHTML = visibleSongs.map(renderSongCard).join("");
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
    render();
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

searchInput.addEventListener("input", (event) => {
  state.query = event.target.value;
  render();
});

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
  state.pickFirst = !state.pickFirst;
  pickFirstToggle.setAttribute("aria-pressed", String(state.pickFirst));
  pickFirstToggle.classList.toggle("chip-active", state.pickFirst);
  render();
});

sortSelect.addEventListener("change", (event) => {
  state.sortKey = event.target.value;
  render();
});

randomAllButton.addEventListener("click", () => {
  renderRandomSong(getRandomSong(state.songs));
});

randomVisibleButton.addEventListener("click", () => {
  renderRandomSong(getRandomSong(getVisibleSongs()));
});

loadSongs();
