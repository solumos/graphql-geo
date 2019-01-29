from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
Session = scoped_session(sessionmaker(autocommit=False, autoflush=False))


def init_db(url: str) -> None:
    """
    Initialize the DB connection by registering models
    :param url: the sqlalchemy engine
    """
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    from geo.models import place

    engine = create_engine(url)
    Session.configure(bind=engine)

    Base.metadata.create_all(bind=engine)
    Base.query = Session.query_property()
