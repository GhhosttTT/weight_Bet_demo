"""
Check if invitations table exists in database
"""
from app.database import engine
from sqlalchemy import inspect


def check_invitations_table():
    """Check if invitations table exists"""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print("Database tables:")
    for table in sorted(tables):
        print(f"  - {table}")
    
    print(f"\n✓ Invitations table exists: {'invitations' in tables}")
    
    if 'invitations' in tables:
        print("\nInvitations table columns:")
        columns = inspector.get_columns('invitations')
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")
        
        print("\nInvitations table indexes:")
        indexes = inspector.get_indexes('invitations')
        for idx in indexes:
            print(f"  - {idx['name']}: {idx['column_names']}")
        
        print("\nInvitations table foreign keys:")
        fks = inspector.get_foreign_keys('invitations')
        for fk in fks:
            print(f"  - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")


if __name__ == "__main__":
    check_invitations_table()
