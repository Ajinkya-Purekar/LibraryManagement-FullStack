from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base


DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/library_db"

engine = create_engine(
    DATABASE_URL,
    echo=True       #shows sql queries in the terminal 
)

SessionLocal = sessionmaker(
    autocommit = False,
    autoflush = False,
    bind = engine
)

Base = declarative_base()



#================ DB DEPENDENCY ======================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

        