import csv
from dataclasses import dataclass
from sqlalchemy import REAL, Boolean, Column, ForeignKey, Integer, MetaData, String, Table, create_engine, func, select
from sqlalchemy.orm import scoped_session, sessionmaker, DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass

@dataclass
class User(Base):
    __tablename__ = 'users'
    name: Mapped[String] = Column(String(50), primary_key=True)

    def __repr__(self):
        return f'<User {self.name!r}>'
    
@dataclass
class Plants(Base):
    __tablename__ = 'plants'
    name: Mapped[String] = Column(String, primary_key=True)
    img_path: Mapped[String] = Column(String(120), unique=True)
    is_invasive: Mapped[Boolean] = Column(Boolean)

    def __repr__(self):
        return f'<Plant {self.name!r}>'
    
@dataclass
class UserPlants(Base):
    __tablename__ = 'user_plants'
    id: Mapped[Integer] = Column(Integer, primary_key=True)
    user: Mapped[Integer] = Column(ForeignKey("users.name"))
    plant: Mapped[Integer] = Column(ForeignKey("plants.name"))
    img_path: Mapped[String] = Column(String(120))
    loc_x: Mapped[REAL] = Column(REAL)
    loc_y: Mapped[REAL] = Column(REAL)

    def __repr__(self):
        return f'<User {self.id}, Plant {self.img_path!r}>'

    
engine = create_engine('sqlite:///foo.db')
db_session = scoped_session(sessionmaker(autocommit=True,
                                         autoflush=False,
                                         bind=engine))
conn = engine.connect()

users = Table('users', Base.metadata, autoload_replace=True)
plants = Table('plants', Base.metadata, autoload_replace=True)
user_plants = Table('user_plants', Base.metadata, autoload_replace=True)

   
def init_db(initial_data_path: str):
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    Base.metadata.create_all(engine)
    Base.metadata.clear()
    Base.metadata.reflect(bind=engine)
    load_initial_data(initial_data_path)

def load_initial_data(initial_data_path: str):
    result = conn.execute(select(func.count()).select_from(plants)).scalar()
    if result != 0:
        return

    with open(initial_data_path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            # Assuming the CSV columns match the table columns
            conn.execute(plants.insert().values(
                name=row['name'],
                img_path=row['img_path'],
                is_invasive=row['is_invasive'] == 'True'
            ))
        conn.commit()

def shutdown():
    db_session.remove()