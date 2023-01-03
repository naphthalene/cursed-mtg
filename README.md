# MTG Inventory

This repo includes SQLAlchemy schemas for magic card inventory
management, automation and scripting. May feature a UI in the
future. Use speech-to-text to capture cards, fuzzy fetch card from
scryfall. Voice commands for inputting is simpler and potentially
quicker than scanning cards.

# Setup

# Pre-requisites

[Download the mtg-json `AllPrintings.sqlite` dataset from
here](https://mtgjson.com/downloads/all-files/#allprintings) into
`data/mtgjson/AllPrintings.sqlite`.

## REPL

Modified IPython shell that lets you query for cards and build decks:

    Œ m_query Card w:text LIKE '%when%dies%create%creature token%'|w:convertedManaCost<=1|w:type LIKE '%creature%'|g:name|o:convertedManaCost

      #     id  name                setCode      power    toughness  manaCost    type                           text
    ---  -----  ------------------  ---------  -------  -----------  ----------  -----------------------------  -----------------------------------------------------------------------------------
      0  24396  Hangarback Walker   EA1              0            0  {X}{X}      Artifact Creature — Construct  Hangarback Walker enters the battlefield with X +1/+1 counters on it.
                                                                                                                When Hanga...
      1   9973  Blisterpod          BFZ              1            1  {G}         Creature — Eldrazi Drone       Devoid (This card has no color.)
                                                                                                                When Blisterpod dies, create a 1/1 colorless El...
      2    819  Doomed Traveler     2X2              1            1  {W}         Creature — Human Soldier       When Doomed Traveler dies, create a 1/1 white Spirit creature token with flying.
      3  30022  Garrison Cat        IKO              1            1  {W}         Creature — Cat                 When Garrison Cat dies, create a 1/1 white Human Soldier creature token.
      4  73566  Grim Initiate       WAR              1            1  {R}         Creature — Zombie Warrior      First strike
                                                                                                                When Grim Initiate dies, amass 1. (Put a +1/+1 counter on an Army y...
      5  27770  Hunted Witness      GRN              1            1  {W}         Creature — Human               When Hunted Witness dies, create a 1/1 white Soldier creature token with lifelin...
      6  31615  Nested Shambler     J21              1            1  {B}         Creature — Zombie              When Nested Shambler dies, create X tapped 1/1 green Squirrel creature tokens, w...
      7   2862  Termagant Swarm     40K              0            0  {X}{G}      Creature — Tyranid             Ravenous (This creature enters the battlefield with X +1/+1 counters on it. If X...
      8  18998  Tukatongue Thallid  CON              1            1  {G}         Creature — Fungus              When Tukatongue Thallid dies, create a 1/1 green Saproling creature token.

    Œ m_show 7
    {'id': 2862,
     'manaCost': '{X}{G}',
     'name': 'Termagant Swarm',
     'power': '0',
     'setCode': '40K',
     'text': 'Ravenous (This creature enters the battlefield with X +1/+1 counters '
             'on it. If X is 5 or more, draw a card when it enters.)\n'
             'Death Frenzy — When Termagant Swarm dies, create a number of 1/1 '
             "green Tyranid creature tokens equal to Termagant Swarm's power.",
     'toughness': '0',
     'type': 'Creature — Tyranid'}

## Deck Builder / Tracking

**WIP** - This isn't built out yet...

Additional tables for tracking which non-proxy cards from inventory are
in existing IRL decks.

Import/export decklists for Moxfield or proxy printing. If all inventory
cards are already in use, compute which proxies need to be printed,
export that list.

TODO:

* Migrations w/alembic
* UI

### Curses UI

**WIP** - This isn't built out yet...

Would be nice to have a terminal interface for building commander decks,
export/import, etc.

# References

## IPython REPL stuff

- https://www.tutorialspoint.com/jupyter/ipython_magic_commands.htm
- https://stackoverflow.com/a/54236701
- https://www.ascii-code.com/
- https://stackoverflow.com/a/51925328
- https://ipython.org/ipython-doc/stable/interactive/reference.html#embedding
- https://ipython.readthedocs.io/en/stable/api/generated/IPython.core.interactiveshell.html#IPython.core.interactiveshell.InteractiveShell
- https://ipython.readthedocs.io/en/stable/api/generated/IPython.terminal.interactiveshell.html#IPython.terminal.interactiveshell.TerminalInteractiveShell
- https://switowski.com/blog/creating-magic-functions-part1/
- https://stummjr.org/post/customize-ipython5-prompt/
- https://ipython.readthedocs.io/en/stable/config/custommagics.html

## SQLAlchemy

- https://docs.sqlalchemy.org/en/20/orm/quickstart.html
- https://docs.sqlalchemy.org/en/20/intro.html#code-examples
- https://docs.sqlalchemy.org/en/20/orm/session_api.html#sqlalchemy.orm.session.Session.params.binds

## Projects

- https://magicthegathering.io
- https://scryfall.com
- https://github.com/EskoSalaka/mtgtools/blob/ca59be9c9eb28d030c1c1d8b9ae74501024fef8f/mtgtools/PCard.py#L560
