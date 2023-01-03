import typing as t

import invoke

import mtg_db.shell as db_shell


@invoke.task(iterable=['commands'])
def repl(
    c: invoke.Context,
    commands: t.List[str] = [],
) -> None:
    del c
    """Start the interactive mtg-db shell."""
    db_shell.shell(commands)
