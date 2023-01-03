import mtg_db.shell as db_shell

def load_ipython_extension(ipython):
    ipython.register_magics(db_shell.MTGShell.Magics(ipython))
