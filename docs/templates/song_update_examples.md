# Song Update Examples

## 부른 횟수 +1

```bash
python tools/update_song.py --title "Lemon" --sing-count +1
```

## 영상 링크 교체

```bash
python tools/update_song.py --title "호랑수월가" --video-url "https://www.youtube.com/watch?v=D92O5JT3E8A"
```

## 가사 링크 추가

```bash
python tools/update_song.py --title "Lemon" --lyrics-url "https://example.com"
```

## 검색 alias 추가

```bash
python tools/update_song.py --title "星の子" --add-tag "별의아이"
```

## 신곡 추가 dry-run

```bash
python tools/append_song.py docs/templates/new_song.example.json --dry-run
```
