import csv
from sqlalchemy import MetaData, Table, create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base

engine = create_engine('sqlite:///foo.db')
metadata = MetaData()
metadata.reflect(engine)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()
conn = engine.connect()

users = Table('users', metadata)
plants = Table('plants', metadata)

def init_db(initial_data_path: str):
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    Base.metadata.create_all(bind=engine)
    load_initial_data(initial_data_path)

def load_initial_data(initial_data_path: str):
    with open(initial_data_path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            # Assuming the CSV columns match the table columns
            engine.execute(plants.insert().values(
                name=row['name'],
                img_path=row['img_path']
            ))

def shutdown():
    db_session.remove()