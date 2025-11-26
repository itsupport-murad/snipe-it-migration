"""
Snipe-IT Migration Helper
Imports SQL backup and uploads to MariaDB inside Coolify network
"""

import pymysql
import os
import sys
import time

# Database connection settings - using internal Coolify network
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'i8ko4k0o48w0kosssoggsg8s'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'user': os.environ.get('DB_USERNAME', 'mariadb'),
    'password': os.environ.get('DB_PASSWORD', 'JWZC24kSc3CaNLjRR6i7fNQOCJImYAUSt3USomIOJeJNZwp6f1zhn8NH0i387BCm'),
    'database': os.environ.get('DB_DATABASE', 'default'),
    'charset': 'utf8mb4',
    'autocommit': True,
    'connect_timeout': 30,
}

# Path to backup file (inside container)
BACKUP_FILE = "/app/backup/snipeit_backup.sql"


def test_connection():
    """Test database connection"""
    print("=" * 50)
    print("  Snipe-IT Migration Helper")
    print("=" * 50)
    print(f"\nConnecting to: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"Database: {DB_CONFIG['database']}")
    print(f"User: {DB_CONFIG['user']}")
    
    try:
        conn = pymysql.connect(**DB_CONFIG)
        print("✅ Connected to MariaDB successfully!")
        
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"   MariaDB Version: {version[0]}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


def clear_database():
    """Clear existing tables before import"""
    print("\n" + "=" * 50)
    print("  Step 1: Clearing existing tables")
    print("=" * 50)
    
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Disable foreign key checks
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        # Get all tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        print(f"   Found {len(tables)} tables to drop")
        
        # Drop each table
        for table in tables:
            table_name = table[0]
            print(f"   Dropping: {table_name}")
            cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")
        
        # Re-enable foreign key checks
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        conn.close()
        print("✅ Database cleared!")
        return True
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        return False


def import_backup():
    """Import the SQL backup file"""
    print("\n" + "=" * 50)
    print("  Step 2: Importing SQL backup")
    print("=" * 50)
    
    if not os.path.exists(BACKUP_FILE):
        print(f"❌ Backup file not found: {BACKUP_FILE}")
        print("   Make sure the backup file is in the /app/backup/ directory")
        return False
    
    file_size = os.path.getsize(BACKUP_FILE) / (1024 * 1024)
    print(f"   File: {BACKUP_FILE}")
    print(f"   Size: {file_size:.2f} MB")
    
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Disable checks during import
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.execute("SET UNIQUE_CHECKS = 0")
        cursor.execute("SET SQL_MODE = 'NO_AUTO_VALUE_ON_ZERO'")
        
        # Read SQL file
        print("   Reading SQL file...")
        with open(BACKUP_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            sql_content = f.read()
        
        # Split into statements
        statements = []
        current_statement = ""
        
        for line in sql_content.split('\n'):
            stripped = line.strip()
            if stripped.startswith('--') or stripped.startswith('/*') or stripped == '':
                continue
            
            current_statement += line + "\n"
            
            if stripped.endswith(';'):
                statements.append(current_statement.strip())
                current_statement = ""
        
        total = len(statements)
        print(f"   Found {total} SQL statements")
        print("   Executing...")
        
        success_count = 0
        error_count = 0
        
        for i, statement in enumerate(statements):
            if not statement or statement == ';':
                continue
                
            try:
                cursor.execute(statement)
                success_count += 1
                
                # Progress indicator every 500 statements
                if (i + 1) % 500 == 0:
                    pct = ((i + 1) / total) * 100
                    print(f"   Progress: {i + 1}/{total} ({pct:.1f}%)")
                    
            except pymysql.Error as e:
                error_count += 1
                if error_count <= 3:
                    short = statement[:80] + "..." if len(statement) > 80 else statement
                    print(f"   ⚠️  Error: {e}")
        
        # Re-enable checks
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        cursor.execute("SET UNIQUE_CHECKS = 1")
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ Import completed!")
        print(f"   Successful: {success_count}")
        print(f"   Errors: {error_count}")
        
        return error_count < 10  # Allow a few errors
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_import():
    """Verify the import by checking tables"""
    print("\n" + "=" * 50)
    print("  Step 3: Verifying import")
    print("=" * 50)
    
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Check important Snipe-IT tables (with stfs_ prefix from backup)
        tables = ['stfs_users', 'stfs_assets', 'stfs_models', 'stfs_categories', 'stfs_locations', 'stfs_settings', 'stfs_manufacturers', 'stfs_suppliers']
        
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
                count = cursor.fetchone()[0]
                print(f"   ✅ {table}: {count} records")
            except:
                print(f"   ❌ {table}: not found")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False


def main():
    """Main function"""
    print("\n🚀 Starting Snipe-IT Migration...")
    print(f"   Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Test connection
    if not test_connection():
        print("\n❌ Cannot connect to database. Exiting.")
        sys.exit(1)
    
    # Clear database
    if not clear_database():
        print("\n❌ Failed to clear database. Exiting.")
        sys.exit(1)
    
    # Import backup
    if not import_backup():
        print("\n❌ Failed to import backup. Exiting.")
        sys.exit(1)
    
    # Verify
    verify_import()
    
    print("\n" + "=" * 50)
    print("  🎉 MIGRATION COMPLETE!")
    print("=" * 50)
    print("\nYou can now access Snipe-IT with your old credentials.")
    print("Don't forget to copy the uploaded files too!\n")


if __name__ == "__main__":
    main()
