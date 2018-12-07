import argparse
from multiprocessing import Pool
from pathlib import Path

import requests
import youtube_dl
from pycaption import DFXPReader, WebVTTReader, WebVTTWriter


def fetch_subtitles(entry, lang='ru'):
    requested_subtitles = entry['automatic_captions']
    if requested_subtitles:
        title = entry['title']
        video_id = entry['id']
        url = requested_subtitles[lang][0]['url']

        text = requests.get(url).content.decode()
        vtt = WebVTTWriter().write(DFXPReader().read(text))

        return video_id, title, vtt

if __name__ == "__main__":
    

    parser = argparse.ArgumentParser()
    parser.add_argument('url', help='video, playlist or channel url')
    parser.add_argument('--dir', default='subtitles')

    args = parser.parse_args()

    Path(args.dir).mkdir(exist_ok=True)
    ydl = youtube_dl.YoutubeDL({'writeautomaticsub': True, 'maxdownloads': 1000, 'playlistend': 100, 'subtitleslangs': ['ru'], 'subtitlesformats': ['ttml']})

    with ydl:
        result = ydl.extract_info(args.url, download=False) 

    if 'entries' in result:
        entries = result['entries']
    else:
        entries = [result]

    with Pool(8) as p:
        subtitles = p.map(fetch_subtitles, entries)

    print(subtitles)
    for id, title, vtt in subtitles:
        with open('{}/{} {}.vtt'.format(args.dir, id, title), 'w') as f:
            f.write(vtt)
