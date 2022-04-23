import sys

from ivycraft.bot.bot import run
from ivycraft.database.database import IvyDB

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "migrations":
            IvyDB().create_migrations()
            exit(0)
        else:
            print("Usage: python -m ivycraft [migrations]")
            exit(1)
    run()
