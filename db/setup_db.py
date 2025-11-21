from create_db import create_db
from drop_db import drop_db
from populate_stocks import populate_stocks
from populate_prices import populate_prices

def populate_db():
    drop_db()
    create_db()
    populate_stocks()
    populate_prices()

if __name__ == "__main__":
    populate_db()