import os
import git

from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database, drop_database

from source.alembic_wrapper import AlembicMigrations


class Database:

    def __init__(self,
                 db_name='alembic',
                 driver='postgresql+psycopg2',
                 login='postgres',
                 password='postgres',
                 host='localhost',
                 port='5432'):

        self.engine = None
        self.url = f'{driver}://{login}:{password}@{host}:{port}/{db_name}'

    @property
    def url(self):
        return self.engine.url

    @url.setter
    def url(self, db_url):
        self.engine = create_engine(db_url)

    def create(self):

        if not database_exists(self.engine.url):
            create_database(self.engine.url)

    def remove(self):

        if database_exists(self.engine.url):
            drop_database(self.engine.url)


class AlembicSession:

    def __init__(self, db_name):
        self.db_name = db_name

        self.db = Database(db_name=db_name)
        self.db.create()

        self.alembic = AlembicMigrations(Database(db_name=db_name).url)
        self.repo = git.Repo('')

    @property
    def branch(self):
        return self.repo.branches[self.db_name]

    def set_active_branch(self):

        # create git branch if not exists
        if self.db_name not in [branch.name for branch in self.repo.heads]:
            self.repo.create_head(self.db_name)

        getattr(self.repo.heads, self.db_name).checkout()
        print(f'GIT: branch switched to: {self.repo.active_branch}')

    def commit(self, name):
        self.repo.index.add(list(self.untracked_files))
        self.repo.index.commit(name)

    def merge(self, first, second):
        first = self.repo.branches[first]
        second = self.repo.branches[second]

        base = self.repo.merge_base(first, second)
        self.repo.index.merge_tree(second, base=base)

        self.repo.index.commit(f'Merge {first.name} -> {second.name}',
                               parent_commits=(first.commit, second.commit))

        self.repo.active_branch.checkout(force=True)

    @property
    def untracked_files(self):

        for file in self.repo.untracked_files:
            if file.startswith('alembic') and not file.endswith('__'):
                yield file