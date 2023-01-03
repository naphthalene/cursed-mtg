import pydantic

class Settings(pydantic.BaseSettings):
    mtg_json_sqlite_uri: str = pydantic.Field(
        default='sqlite:///data/mtgjson/AllPrintings.sqlite',
        env='MTG_JSON_SQLITE_URI'
    )
    inventory_sqlite_uri: str = pydantic.Field(
        default='sqlite:///data/inventory.sqlite',
        env='INVENTORY_SQLITE_URI'
    )
