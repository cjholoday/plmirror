import sys
import json


import click


@click.command()
@click.argument('playlist_names', nargs=-1)
def main(playlist_names):
    config = None
    try:
        with open('config.json') as config_file:
            config = json.load(config_file)
    except FileNotFoundError:
        print("Error: config.json not found", file=sys.stderr)
        sys.exit(1)

    # check that playlist names have a configuration and url before starting
    for pl_name in playlist_names:
        print(pl_name)
        if pl_name not in config['playlists']:
            print("Error: playlist with name '{}' not found in config.json"
                  .format(pl_name))
            sys.exit(1)
        elif 'url' not in config['playlists'][pl_name]:
            print("Error playlist with name '{}' has no configured url"
                  .format(pl_name))
            sys.exit(1)

    print(config)
    print(playlist_names)

if __name__ == '__main__':
    main()
