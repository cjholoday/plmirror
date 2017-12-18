# Plmirror

## Prerequisites

```
python3
youtube-dl
```

For installing youtube-dl, see https://github.com/rg3/youtube-dl 

## Usage

On startup, ```plmirror``` looks for a ```config.json``` file in the currrent working directory. ```config.json``` specifies which playlists to mirror by url, the file format (mp3 for audio or mp4 for video), and the directory in which to put the playlist.

If ```plmirror``` is run with the same ```config.json``` only newly added videos will be added to the playlist directories. **However, new videos will only be added if you set the following on your youtube playlists**: "Add new videos to top of playlist." ```plmirror``` works only on public playlists.

```
$ cd plmirror/example
$ python3 plmirror.py
```