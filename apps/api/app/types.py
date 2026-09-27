from sqlalchemy.types import JSON, TypeDecorator


class JSONVariant(TypeDecorator):
    """JSONB on PostgreSQL, JSON elsewhere (SQLite tests)."""

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            from sqlalchemy.dialects.postgresql import JSONB

            return dialect.type_descriptor(JSONB())
        return dialect.type_descriptor(JSON())
