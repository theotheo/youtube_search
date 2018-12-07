import argparse
import datetime as dt
from pathlib import Path

import pandas as pd
import youtube_dl
from pycaption import DFXPReader, WebVTTReader, WebVTTWriter


def vtt_to_df(fn):
    """
    Convert vtt to DataFrame

    args:
        fn - filepath to .vtt-file

    returns:
        DataFrame
    """

    with open(fn) as f:
        text = f.read()
        
    vtt = WebVTTReader().read(text)
    
    subtitles = []
    for caption in vtt.get_captions('en-US'):
        subtitles.append({
            'time': dt.datetime.strptime(caption.format_start(), '%H:%M:%S.%f').strftime('%-Hh%mm%Ss'), 
            'start': int((dt.datetime.strptime(caption.format_start(), '%H:%M:%S.%f') - dt.datetime(1900,1,1)).total_seconds()),
            'duration': (caption.end - caption.start) /100000,
            'text': caption.get_text()
        })
        
    df = pd.DataFrame(subtitles)
    return df
    

def vtts_to_df(dir):
    """Convert vtt-files to DataFrame.
    
    args:
        dir - directory contains .vtt-files, downloaded from youtube, with name like '$id $title.vtt'
        
    returns:
        DataFrame
    """
    
    videos = []
    
    ydl = youtube_dl.YoutubeDL({'maxdownloads': 10000, 'playlistend': 100})
    with ydl:
        for fn in Path(dir).glob('*.vtt'):
            df = vtt_to_df(str(fn))
            text = ' '.join(sum(df['text'].str.split(), []))

            id = str(fn.stem).split(' ')[0]
            res = ydl.extract_info(id, download=False)
            del res['formats']
            del res['requested_formats']
            res['text'] = text
            
            videos.append(res)
        
    df = pd.DataFrame(videos)
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', help='.vtt directory', default='subtitles')

    args = parser.parse_args()

    df = vtts_to_df(args.dir)

    df.to_json('{}.jsonlines'.format(Path(args.dir).name), orient='records', lines=True)
