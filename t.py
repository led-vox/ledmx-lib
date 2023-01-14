from pathlib import Path

import yaml

from ledmx.multiverse import Multiverse

if __name__ == '__main__':
    yaml_test = Path('layout.yaml').read_text()
    layout = yaml.safe_load(yaml_test)
    mvs = Multiverse(layout)
    mvs[407] = 5, 8, 9
    pass