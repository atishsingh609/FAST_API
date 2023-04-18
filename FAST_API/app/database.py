from sqlalchemy import create_engine
from urllib.parse import quote_plus
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQL_ALCHEMY_URL = "postgresql://<username>:<password>@<ip-address/hostname>/databasename"

SQL_ALCHEMY_URL = "postgresql://postgres:%s@localhost/fastapi"

engine = create_engine(SQL_ALCHEMY_URL % quote_plus("Jaiparshuram@12"))
sessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()
