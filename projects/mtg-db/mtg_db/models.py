import sqlalchemy as sa

import sqlalchemy.ext.automap as automap
import sqlalchemy.orm as orm

import mtg_db.config as db_config


# Instantiate settings
settings = db_config.Settings()

# Create engines
engines = dict(
    mtg_json=sa.create_engine(settings.mtg_json_sqlite_uri),
    inventory=sa.create_engine(settings.inventory_sqlite_uri),
)

# --------------------------------------------------
# Reflect mtg_json card db
Base = automap.automap_base()
Base.prepare(autoload_with=engines['mtg_json'])

# Reflected Models
Card = Base.classes.cards
Set = Base.classes.sets
Legality = Base.classes.legalities
Ruling = Base.classes.rulings
ForeignData = Base.classes.foreign_data
Meta = Base.classes.meta
SetTranslation = Base.classes.set_translations
Token = Base.classes.tokens

_MTG_JSON_MODELS = [
    Card,
    Set,
    Legality,
    Ruling,
    ForeignData,
    Meta,
    SetTranslation,
    Token,
]


# --------------------------------------------------
# Declarative Models
DeclBase = orm.declarative_base()

# class Copy(DeclBase):
#     """A copy of a specific card."""
#     __tablename__ = "copies"  # name of the SQL table

#     id = sa.Column(sa.Integer, primary_key=True)
#     card = orm.relationship(
#         "Card", back_populates="copies"
#     )

# class Deck(DeclBase):
#     """."""
#     pass

# --------------------------------------------------
# Routing session
class RoutingSession(orm.Session):
    def get_bind(self, mapper=None, clause=None):
        del clause  # unused
        if mapper and any([
            m for m in _MTG_JSON_MODELS
            if issubclass(mapper.class_, m)
        ]):
            return engines['mtg_json']
        return engines['inventory']
