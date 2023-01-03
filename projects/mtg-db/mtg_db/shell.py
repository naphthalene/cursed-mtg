# import pathlib as paths
import pprint as pp
import re
import subprocess as sp
import typing as t
import traitlets.config as tc
import urllib.parse as urls

import IPython
import IPython.core.magic as im
import IPython.terminal.prompts as ip
import sqlalchemy as sa
import sqlalchemy.orm as orm
import tabulate

import mtg_db.models as models
import mtg_db.config as config


class MTGShell:
    """The interactive experience."""

    def __init__(
        self, cfg: config.Settings, commands: t.List[str] = []
    ) -> None:
        """Create a shell instance."""
        self.config: config.Settings = cfg
        self.s: orm.Session = (
            orm.sessionmaker(class_=models.RoutingSession)()
        )
        # Override this at any time to change displayed table
        self.cols = dict(
            cards=['id', 'name', 'setCode', 'power',
                   'toughness', 'manaCost', 'type', 'text',],
            sets=['id', 'code', 'block', 'name', 'releaseDate',],
        )
        self.initial_commands = commands
        self.result_type: t.Optional[t.Type] = None
        self.rows = []

    def __call__(self, *args, **kwargs):
        """Main interactive entrypoint."""
        del args, kwargs
        # Simulate the "embed" call by injecting the locals and globals
        IPython.start_ipython(
            argv=[], config=self.ipython_config,
            user_ns={**locals(), **globals()}
        )

    @property
    def ipython_config(self) -> t.Any:
        """Create a config to be passed into IPython initializer."""
        c: t.Any = tc.Config()

        # Add reference to this object
        c.mtg_shell = self

        # Configure the shell
        c.TerminalIPythonApp.display_banner = False
        c.InteractiveShellApp.exec_lines = [
            '%load_ext autoreload',
            '%autoreload 2',
            '%load_ext mtg_db',
        ] + self.initial_commands
        c.InteractiveShell.confirm_exit = False
        c.InteractiveShell.prompts_class = self.CustomPrompt
        return c

    def table(
        self,
        *,
        rows: t.List,
        cols: t.List[str],
        max_column_width: int = 80,
        clamp: bool = True,
    ):
        """Pretty-print rows of given model."""
        def clamp_width(value: t.Any):
            """Limit the width of string column when printing."""
            if (
                clamp
                and isinstance(value, str)
                and len(value) > max_column_width
            ):
                return value[:max_column_width] + '...'
            return value

        print('\n' + tabulate.tabulate(
            [
                [i] + [clamp_width(r.__dict__[p]) for p in cols]
                for i, r in enumerate(rows)
            ],
            headers=['#'] + cols
        ))

    @im.magics_class
    class Magics(im.Magics):
        def __init__(self, shell):  # type: ignore
            """Create a stateful class with embedded additional values."""
            super().__init__(shell)
            self.m: MTGShell = shell.config.mtg_shell

        @im.line_magic
        def m_help(self, line) -> None:
            """
            This help message.
            """
            del line
            print(
                'All of these are line magics, using [%]m_<command> <input>\n\n'
                'Available MTG magics:\n'
            )
            cls = self.__class__
            for attr in dir(cls):
                if attr.startswith('m_'):
                    method = getattr(cls, attr)
                    print(f'  {attr} {method.__doc__.rstrip()}')

        @im.line_magic
        def m_debug(self, line) -> None:
            """
            Drop to a debugger shell.
            """
            breakpoint()  # no-qa
            del line

        @im.line_magic
        def m_sql(self, line) -> None:
            """<db_alias>
            Drops to a sqlite3 shell for given db alias.
            """
            mj = urls.urlparse(self.m.config.mtg_json_sqlite_uri).path
            inv = urls.urlparse(self.m.config.inventory_sqlite_uri).path
            # Bind multiple aliases to each db
            db_aliases = {
                **{n: mj for n in ['m', 'mj', 'mtgjson', 'mtg-json']},
                **{n: inv for n in ['i', 'in', 'inv', 'inventory']},
            }
            if any([db in line for db in db_aliases.keys()]):
                sp.run(['sqlite3', db_aliases[line.strip()]])
            else:
                raise ValueError(f'Invalid db alias: [{line}]')

        @im.line_magic
        def m_query(self, line) -> None:
            """<Model> <w:<where>|l:<limit>|g:<group_by>|o:<order_by>...>
            Simple database select w/filters for whatever.
            """
            query_regex = r'^([a-zA-Z0-9]+) ?(.*)?$'
            if not (match := re.match(query_regex, line)):
                raise ValueError(f'Invalid command: {line}')
            # Grab the class from the imported 'models' module
            model = getattr(models, match.group(1))
            # RoutingSession creates query against correct db automatically
            query = self.m.s.query(model)
            if (clauses := match.group(2)):
                for clause in clauses.split('|'):
                    instruction, content = clause.split(':')
                    if instruction == 'w':
                        query = query.filter(
                            sa.text(f'{model.__name__}.{content}')
                        )
                    elif instruction == 'l':
                        query = query.limit(int(content))
                    elif instruction == 'g':
                        query = query.group_by(sa.text(content))
                    elif instruction == 'o':
                        query = query.order_by(sa.text(content))

            self.m.result_type = model
            self.m.rows = query.all()
            self.m.table(
                rows=self.m.rows,
                # By default, show all columns,
                # unless otherwise defined in self.cols
                cols=self.m.cols.get(
                    model.__name__,
                    model.__table__.columns.keys()
                )
            )

        @im.line_magic
        def m_show(self, line):
            """<row_number>
            Print details about given result row from previous query.
            """
            def filter_cols(result_type: t.Type, k: str):
                """Select columns to display, or show all if undefined."""
                cols = self.m.cols.get(result_type.__name__)
                return not cols or k in cols
            try:
                row_num = int(line.strip())
                extant_rows = len(self.m.rows)
                assert bool(self.m.rows), 'No results'
                assert self.m.result_type, 'No result type'
                assert row_num >= 0 and row_num < extant_rows, 'Not in range'
            except (ValueError, AssertionError) as e:
                print('Please enter a valid row number:\n', e)
            else:
                pp.pprint({
                    k: v for k, v
                    in self.m.rows[row_num].__dict__.items()
                    if filter_cols(self.m.result_type, k)
                })

        @im.line_magic
        def m_cols(self, line):
            """<Model>
            Print default and available columns for given model.
            """
            try:
                model = getattr(models, line.strip())
                print(
                    'Available: '
                    f'[{", ".join([c.name for c in model.__table__.columns])}]'
                )
                print(
                    'Shown: '
                    f'[{", ".join(self.m.cols.get(model.__table__.name, []))}]'
                )
            except AttributeError as e:
                print('Please enter a valid model name:\n', e)

        @im.line_magic
        def m_import(self, line):
            """<file_path>
            Import a setlist from a path.
            """
            raise NotImplementedError()

    class CustomPrompt(ip.Prompts):
        def in_prompt_tokens(self, cli=None) -> t.List:
            """Custom prompt tokens."""
            del cli  # unused
            return [(ip.Token.Foo, 'Œ '),]  # type: ignore

def shell(commands):
    MTGShell(config.Settings(), commands)()
