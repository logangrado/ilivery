#!/usr/bin/env python3

from pathlib import Path
import click

import logging

logger = logging.getLogger(__name__)


def _load_config(config_path):
    logger.info("Loading config")
    from ilivery.config.livery_config import LiveryConfig

    config_path = Path(config_path)

    if config_path.suffix == ".jsonnet":
        import _jsonnet
        import json

        config = json.loads(_jsonnet.evaluate_file(str(config_path)))
    else:
        raise ValueError(f"Unknown suffix: {config_path.suffix}")

    config = LiveryConfig.model_validate(config)
    return config


@click.command()
@click.argument("config", type=click.Path())
@click.option("--no-cache", is_flag=True)
@click.option("--show", is_flag=True)
@click.option("--show-spec", is_flag=True)
@click.option("--save", is_flag=True)
def main(config, no_cache, show, show_spec, save):
    config = _load_config(config)

    from ilivery.build_livery import build_livery
    from ilivery import utils

    no_cache = True
    livery = build_livery(config, no_cache)

    if show_spec:
        livery._livery.show_spec()
    if show:
        livery._livery.show()

    if save and utils.os.in_wsl():
        livery.save()


if __name__ == "__main__":
    main()
