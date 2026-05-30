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
  query: ""
};

const searchInput = document.querySelector("#search-input");
const resultSummary = document.querySelector("#result-summary");
const songList = document.querySelector("#song-list");
const randomAllButton = document.querySelector("#random-all-button");
const randomVisibleButton = document.querySelector("#random-visible-button");
const randomResult = document.querySelector("#random-result");

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

function getVisibleSongs() {
  return state.songs.filter((song) => matchesSearch(song, state.query));
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
        <span>♪</span>
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

  resultSummary.textContent = state.query
    ? `${visibleSongs.length}곡이 검색되었습니다.`
    : `전체 ${visibleSongs.length}곡`;

  if (visibleSongs.length === 0) {
    songList.innerHTML = `<p class="empty-message">조건에 맞는 곡이 없습니다.</p>`;
    return;
  }

  songList.innerHTML = visibleSongs.map(renderSongCard).join("");
}

async function loadSongs() {
  try {
    const response = await fetch("./data/songs.json");
    if (!response.ok) {
      throw new Error(`songs.json load failed: ${response.status}`);
    }

    state.songs = await response.json();
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

randomAllButton.addEventListener("click", () => {
  renderRandomSong(getRandomSong(state.songs));
});

randomVisibleButton.addEventListener("click", () => {
  renderRandomSong(getRandomSong(getVisibleSongs()));
});

loadSongs();
