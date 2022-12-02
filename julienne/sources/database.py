from typing import Any
from typing import Dict
from typing import List

import sqlparse
from pypyodbc import Connection

from julienne.exceptions import MissingSelectClauseException
from julienne.exceptions import MoreThanOneStatementException
from julienne.sources.base import DataSource


class ExtractQuery:
    sql: str

    def __init__(self, sql: str) -> None:
        self.sql = sql

    @property
    def keys(self) -> List[str]:
        statements = sqlparse.parse(self.sql)
        if len(statements) != 1:
            raise MoreThanOneStatementException(
                "There must be exactly one SQL statement!"
            )
        parsed_sql: sqlparse.sql.Statement = statements[0]
        select_statements = [x for x in parsed_sql.tokens if str(x).lower() == "select"]
        return [x.get_name() for x in select_statements[0]]


class ExtractQueryDataSource(DataSource):
    extract_query: ExtractQuery
    connection: Connection

    def __init__(self, extract_query: ExtractQuery, connection: Connection):
        self.extract_query = extract_query
        self.connection = connection

    def __iter__(self):
        self.cursor = self.connection.cursor()
        self.result = self.cursor.execute(self.extract_query.sql)
        assert self.cursor.description is not None
        self.columns = [x[0] for x in self.cursor.description]
        return self

    def __next__(self) -> Dict[str, Any]:
        row = self.cursor.fetchone()
        if row is not None:
            return dict(zip(self.columns, row))
        raise StopIteration
