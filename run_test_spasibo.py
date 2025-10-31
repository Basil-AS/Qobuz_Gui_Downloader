from core.lyrics_search import LyricsSearcher
import logging

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
searcher = LyricsSearcher()
print('=== TEST: СПАСИБО "репетиция, ноябрь 2006" ===')
plain, lrc = searcher.search_lyrics('Земфира', 'СПАСИБО "репетиция, ноябрь 2006"', 'Спасибо', 257)
print(f'Plain found: {bool(plain)}')
print(f'LRC found: {bool(lrc)}')
if plain:
    print('\nPlain snippet:\n', plain[:400])
if lrc:
    print('\nLRC snippet:\n', lrc[:400])
