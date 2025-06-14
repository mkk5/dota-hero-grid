from settings_model import ConfigSettings, CategorySettings, ColumnSettings
from sources.file.model import Category, Config, HeroGrid
from itertools import batched
from typing import Protocol, Any


class Source(Protocol):
    def __call__(self, param: Any) -> list[int]:
        """Source protocol"""

type SourceDict = dict[str, Source]


def get_category_height(width_px: float, width_heroes: int, heroes_number: int) -> float:
    card_width, card_height, padding2 = (51.304352, 82.608699, 8.695647) # TODO: review & document
    height_heroes = -(-heroes_number//width_heroes) if heroes_number else 1 # div up (min 1)
    height = (card_height*height_heroes+padding2) * width_px / (card_width*width_heroes+padding2)
    return height

def create_category(category_opts: CategorySettings, column_opts: ColumnSettings, y: float, f: SourceDict) -> Category:
    hero_ids = f[category_opts.source](category_opts.param)
    height = get_category_height(column_opts.width, column_opts.width_heroes, len(hero_ids))
    return Category(
        category_name=category_opts.name,
        x_position=column_opts.x,
        y_position=y,
        width=column_opts.width,
        height=height,
        hero_ids=hero_ids
    )

def create_config(config_opts: ConfigSettings, f: SourceDict) -> Config:
    columns_opts = config_opts.columns
    row_gap = config_opts.row_gap
    y = 0
    categories = []
    for row_category_opts in batched(config_opts.categories, len(columns_opts)):
        row = [create_category(category_s, column_s, y, f) for category_s, column_s in zip(row_category_opts, columns_opts)]
        y = y + max(c.height for c in row) + row_gap
        categories.extend(row)
    return Config(config_name=config_opts.name, categories=categories)

def create_grid(configs: list[ConfigSettings], factory: SourceDict) -> HeroGrid:
    new_configs = [create_config(config_settings, factory) for config_settings in configs]
    return HeroGrid(configs=new_configs)
