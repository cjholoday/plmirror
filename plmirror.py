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


    print(config)
    print(playlist_names)

if __name__ == '__main__':
    main()
