from app.db.base import Base
from app.db.session import engine
from app.models.internship import Internship
from app.models.profile import Profile

def main():
    tables = [Internship.__tablename__, Profile.__tablename__]
    Base.metadata.create_all(bind=engine)
    print(f"Created tables: {', '.join(tables)}")

if __name__ == "__main__":
    main()