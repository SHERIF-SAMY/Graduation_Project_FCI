from sqlalchemy import text
from sql.db import get_engine

def execute_query(sql_query: str, params: dict = None) -> list:
    """
    Executes a read-only parameterized query and returns rows as dictionaries.
    """
    if params is None:
        params = {}
    
    # Basic check to enforce read-only
    lower_query = sql_query.lower()
    if any(keyword in lower_query for keyword in ["insert ", "update ", "delete ", "drop ", "exec ", "execute "]):
        raise ValueError("Only read-only SELECT queries are allowed.")
        
    engine = get_engine()
    with engine.connect() as connection:
        result = connection.execute(text(sql_query), params)
        # Using _mapping to convert Row to dict in SQLAlchemy 2.0+
        return [dict(row._mapping) for row in result.fetchall()]
