const searchableFields = [
  "title",
  "translation",
  "artist",
  "artistKr",
  "language",
  "genre",
  "theme",
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

function createLinkButton(url, label) {
  if (!url) {
    return `<span class="button button-disabled" aria-disabled="true">📄 가사 준비 중</span>`;
  }

  return `<a class="button" href="${url}" target="_blank" rel="noopener noreferrer">${label}</a>`;
}

function renderSongCard(song) {
  const pickBadge = song.pick ? `<span class="pick-badge">🍵 Pick</span>` : "";
  const translatedTitle = song.translation
    ? `<p class="song-translation">${song.translation}</p>`
    : "";
  const artistMeta = [song.artistKr, song.language].filter(Boolean).join(" · ");
  const themeText = [song.genre, song.theme].filter(Boolean).join(" · ");
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
      <div class="song-card-header">
        <div>
          <h3>${song.title}</h3>
          ${translatedTitle}
        </div>
        ${pickBadge}
      </div>
      <p class="song-artist">${song.artist}${artistMeta ? ` · ${artistMeta}` : ""}</p>
      <p class="song-theme">${themeText}</p>
      ${sourceNote}
      <div class="song-actions">
        ${videoButton}
        ${lyricsButton}
        ${singCount}
      </div>
    </article>
  `;
}

function render() {
  const visibleSongs = getVisibleSongs();

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

loadSongs();
