from sqlalchemy.orm import Session


def execute_raw_query(db: Session, query: str):
    """
    Optional helper for raw SQL execution.
    Not used yet in Phase 1; kept for future use.
    """
    result = db.execute(query)
    return result.fetchall()
