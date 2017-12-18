#!/usr/bin/env python3
import sys
import json
import subprocess
import os


# Used as a download template for youtube-dl. pl_name and pl_idx are substituted
# by plmirror while the title, uploader_id, and ext are handled by youtube-dl
OUTPUT_TEMPLATE = "{pl_name}/{pl_idx:03d}__%(title)s__%(uploader)s__%(id)s.%(ext)s"


def mirror_playlist(pl_name, pl_config):
    # create our playlist directory if it doesn't exist already
    mirror_dir = os.path.join(os.getcwd(), pl_name)
    if not os.path.exists(mirror_dir):
        os.makedirs(mirror_dir)

    try:
        print("[plmirror] Discovering new videos...")
        cmd = ['youtube-dl', pl_config['url']]

        # ignore videos that have been deleted / are unavailable
        cmd.extend(['--ignore-errors'])

        # only notify us of new videos
        cmd.extend(
            ['--download-archive', os.path.join(mirror_dir, 'archive.txt')])

        # do not download anything, only get video id's
        cmd.append('--get-id')

        raw_ids = subprocess.check_output(cmd)
    except subprocess.CalledProcessError as err:
        # youtube-dl will throw an error if a video was deleted. We must ignore
        # it if we want to be tolerant of missing videos
        raw_ids = err.output

    # We're done if there are no new videos
    if not raw_ids:
        print("[plmirror] No new videos for playlist '{}'".format(pl_name))
        return

    vid_ids = raw_ids.decode('utf-8').strip().split('\n')

    # discover highest playlist index
    pl_idx = -1
    for entry in os.listdir(mirror_dir):
        if len(entry) < 3:
            print("[plmirror] Rogue file '{}' in playlist directory '{}'"
                  .format(entry, mirror_dir), file=sys.stderr)
            sys.exit(1)

        # We only care about playlist entries for determining the idx
        if entry == 'archive.txt':
            continue

        try:
            pl_idx = max(int(entry[:3]), pl_idx)
        except ValueError:
            print("[plmirror] Rogue file '{}' in playlist directory '{}'"
                  .format(entry, mirror_dir), file=sys.stderr)
            sys.exit(1)
    pl_idx += 1

    with open(os.path.join(mirror_dir, 'archive.txt'), 'a') as archive:
        # download backwards so that videos are ordered like they are on youtube
        for vid_id in reversed(vid_ids):
            print("[plmirror] Downloading video with id '{}'".format(vid_id))
            output_format = OUTPUT_TEMPLATE.format(
                pl_name=pl_name, pl_idx=pl_idx)
            cmd = ['youtube-dl',
                   'https://www.youtube.com/watch?v={}'.format(vid_id)]
            cmd.extend(['-o', output_format])
            if pl_config['type'] == 'audio':
                cmd.append('--extract-audio')
                cmd.append('--prefer-ffmpeg')
                cmd.extend(['--audio-format', 'mp3'])
                cmd.extend(['--audio-quality', '0'])
            else:
                cmd.extend(['--recode-video', 'mp4'])

            try:
                subprocess.check_call(cmd)
            except subprocess.CalledProcessError:
                print("[plmirror] Error: failed to mirror video with id '{}'"
                      .format(vid_id))
                continue

            # commit this video to our mirror
            pl_idx += 1
            archive.write('youtube {}\n'.format(vid_id))


def main():
    try:
        config = None
        with open('config.json') as config_file:
            config = json.load(config_file)
    except FileNotFoundError:
        print("[plmirror] Error: config.json not found", file=sys.stderr)
        sys.exit(1)

    validate_config(config)

    for pl_name in config['playlists']:
        print("[plmirror] Mirroring playlist '{}'".format(pl_name))
        mirror_playlist(pl_name, config['playlists'][pl_name])


def validate_config(config):
    playlists = config['playlists']
    for pl_name in playlists:
        if 'url' not in playlists[pl_name]:
            print("[plmirror] Error: playlist with name '{}' has no configured url"
                  .format(pl_name), file=sys.stderr)
            sys.exit(1)
        if 'type' not in playlists[pl_name]:
            print("[plmirror] Error: playlist '{}' has no type "
                  "(options: 'audio' or 'video')" .format(pl_name), file=sys.stderr)
            sys.exit(1)
        if playlists[pl_name]['type'] not in ['audio', 'video']:
            print("[plmirror] Error: playlist '{}' has an invalid type '{}' "
                  "(options: 'audio' or 'video')", file=sys.stderr)
            sys.exit(1)


if __name__ == '__main__':
    main()
