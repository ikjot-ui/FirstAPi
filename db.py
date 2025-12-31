from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

db_url = "postgresql://GEODBD_AUSR:GEODBD_ADMIN3256@103.239.89.100:5432/GEO_DB_DEV"
engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

