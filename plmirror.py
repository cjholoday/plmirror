import sys
import json
import subprocess
import os


# Used as a download template for youtube-dl. pl_name and pl_idx are substituted
# by plmirror while the title, uploader_id, and ext are handled by youtube-dl
OUTPUT_TEMPLATE = "{pl_name}/{pl_idx:03d}__%(title)s__%(uploader_id)s.%(ext)s"

def mirror_playlist(pl_name, pl_config):
    # create our playlist directory if it doesn't exist already
    mirror_dir = os.path.join(os.getcwd(), pl_name)
    if not os.path.exists(mirror_dir):
        os.makedirs(mirror_dir)


    try:
        print("\tDiscovering new videos...")
        cmd = ['youtube-dl', pl_config['url']]

        # only notify us of new videos
        cmd.extend(['--download-archive', os.path.join(mirror_dir, 'archive.txt')])

        # do not download anything, only get video id's
        cmd.append('--get-id')

        # TODO: handle this
        cmd.append('--ignore-errors')
        raw_ids = subprocess.check_output(cmd)
    except subprocess.CalledProcessError as err:
        # TODO: test/handle this
        raw_ids = err.output

    # We're done if there are no new videos
    if not raw_ids:
        print("\tNo new videos for playlist '{}'".format(pl_name))
        return

    print(raw_ids)
    vid_ids = raw_ids.decode('utf-8').strip().split('\n')

    # TODO: discover highest playlist number
    pl_idx = 0
    
    print(vid_ids)
    with open(os.path.join(mirror_dir, 'archive.txt'), 'a') as archive:
        for vid_id in vid_ids:
            print("\tDownloading video with id '{}'".format(vid_id))
            output_format = OUTPUT_TEMPLATE.format(pl_name=pl_name, pl_idx=pl_idx)
            cmd = ['youtube-dl', 'https://www.youtube.com/watch?v={}'.format(vid_id)]
            cmd.extend(['-o', output_format])
            if pl_config['type'] == 'audio':
                cmd.append('--extract-audio')
                cmd.append('--prefer-ffmpeg')
                cmd.extend(['--audio-format', 'mp3'])
                cmd.extend(['--audio-quality', '0'])
            try:
                subprocess.check_call(cmd)
            except subprocess.CalledProcessError:
                print("\tError: failed to mirror video with id '{}'".format(vid_id))
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
        print("Error: config.json not found", file=sys.stderr)
        sys.exit(1)

    validate_config(config)

    for pl_name in config['playlists']:
        print("Mirroring playlist '{}'".format(pl_name))
        mirror_playlist(pl_name, config['playlists'][pl_name])

def validate_config(config):
    playlists = config['playlists']
    for pl_name in playlists:
        if 'url' not in playlists[pl_name]:
            print("Error: playlist with name '{}' has no configured url"
                  .format(pl_name), file=sys.stderr)
            sys.exit(1)
        if 'type' not in playlists[pl_name]:
            print("Error: playlist '{}' has no type (options: 'audio' or 'video')"
                  .format(pl_name), file=sys.stderr)
            sys.exit(1)
        if playlists[pl_name]['type'] not in ['audio', 'video']:
            print("Error: playlist '{}' has an invalid type '{}' "
                    "(options: 'audio' or 'video')", file=sys.stderr)
            sys.exit(1)

if __name__ == '__main__':
    main()
