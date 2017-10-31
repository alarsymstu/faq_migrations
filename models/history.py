from sqlalchemy import Column, Integer, String
from . import Base, db_session, engine, MetaData


class VersionHistory(Base):
    __tablename__ = 'alembic_version_history'

    id = Column(Integer, primary_key=True)
    previous_revision = Column(String)
    forward_revision = Column(String)

    def __init__(self, previous_revision, forward_revision):
        self.previous_revision = previous_revision
        self.forward_revision = forward_revision

    def check_for_copy(self):
        result = db_session.query(self)\
            .filter(VersionHistory.forward_revision == self.forward_revision)\
            .filter(VersionHistory.previous_revision == self.previous_revision)\
            .first()

        return True if result else False

    def list(self, offset=0, limit=0):
        return db_session.query(self)\
            .filter()\
            .order_by(VersionHistory.id.desc()) \
            .offset(offset) \
            .limit(limit)

    def save(self):

        if not engine.dialect.has_table(engine, self.__tablename__):
            metadata = MetaData(engine)
            metadata.create_all()

        if self.check_for_copy():
            db_session.add(self)
            db_session.commit()

            return True

        return False

    def __repr__(self):
        return f"<Version({id}) {self.previous_revision} -> " \
               f"{self.forward_revision}>"