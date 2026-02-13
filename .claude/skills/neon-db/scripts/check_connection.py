#!/usr/bin/env python3
"""Check Neon database connection and display diagnostics.

Usage:
    python check_connection.py
    python check_connection.py --verbose
"""
import argparse
import os
import sys
from urllib.parse import urlparse

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def check_env_var() -> str | None:
    """Check if DATABASE_URL is set."""
    url = os.getenv("DATABASE_URL")
    if not url:
        print("❌ DATABASE_URL environment variable not set")
        print("\nFix: Add DATABASE_URL to your .env file:")
        print("  DATABASE_URL=postgresql://user:pass@host/db?sslmode=require")
        return None
    print("✓ DATABASE_URL is set")
    return url


def parse_url(url: str, verbose: bool = False) -> bool:
    """Parse and validate the connection URL."""
    try:
        parsed = urlparse(url)

        if verbose:
            print(f"\nConnection details:")
            print(f"  Scheme:   {parsed.scheme}")
            print(f"  Host:     {parsed.hostname}")
            print(f"  Port:     {parsed.port or 5432}")
            print(f"  Database: {parsed.path[1:]}")
            print(f"  User:     {parsed.username}")
            print(f"  SSL:      {'sslmode' in (parsed.query or '')}")

        if parsed.scheme != "postgresql":
            print(f"❌ Invalid scheme: {parsed.scheme} (expected 'postgresql')")
            return False

        if not parsed.hostname:
            print("❌ Missing hostname")
            return False

        if "sslmode=require" not in (parsed.query or ""):
            print("⚠️  Warning: sslmode=require not in URL (required for Neon)")

        print("✓ URL format is valid")
        return True

    except Exception as e:
        print(f"❌ Failed to parse URL: {e}")
        return False


def test_connection(url: str, verbose: bool = False) -> bool:
    """Test the database connection."""
    try:
        from sqlalchemy import create_engine, text

        print("\nTesting connection...")
        engine = create_engine(url, echo=verbose)

        with engine.connect() as conn:
            # Test basic connectivity
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
            print("✓ Basic connection successful")

            # Get PostgreSQL version
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✓ PostgreSQL version: {version.split(',')[0]}")

            # Get current database
            result = conn.execute(text("SELECT current_database()"))
            db_name = result.fetchone()[0]
            print(f"✓ Connected to database: {db_name}")

            # List tables
            result = conn.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            if tables:
                print(f"✓ Tables found: {', '.join(tables)}")
            else:
                print("ℹ️  No tables in public schema")

        return True

    except ImportError:
        print("❌ sqlalchemy not installed")
        print("   Run: pip install sqlalchemy psycopg2-binary")
        return False

    except Exception as e:
        print(f"❌ Connection failed: {e}")

        # Provide helpful error messages
        error_str = str(e).lower()
        if "authentication failed" in error_str:
            print("\n💡 Fix: Check your username and password")
        elif "could not connect" in error_str or "connection refused" in error_str:
            print("\n💡 Fix: Check hostname and network connectivity")
        elif "does not exist" in error_str:
            print("\n💡 Fix: Check database name")
        elif "ssl" in error_str:
            print("\n💡 Fix: Add ?sslmode=require to your URL")

        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Check Neon database connection"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed output"
    )

    args = parser.parse_args()

    print("=" * 50)
    print("Neon Database Connection Check")
    print("=" * 50)
    print()

    # Step 1: Check environment variable
    url = check_env_var()
    if not url:
        sys.exit(1)

    # Step 2: Parse URL
    if not parse_url(url, args.verbose):
        sys.exit(1)

    # Step 3: Test connection
    if not test_connection(url, args.verbose):
        sys.exit(1)

    print()
    print("=" * 50)
    print("✅ All checks passed! Database is ready.")
    print("=" * 50)


if __name__ == "__main__":
    main()
