"""
Helper script to create .env file with correct database configuration
"""
import os

# Database configuration
DB_TYPE = "mysql"
# Update these values according to your XAMPP setup
DB_HOST = "127.0.0.1"  # or "localhost"
DB_PORT = "3306"  # XAMPP default is 3306, but some use 3307
DB_USER = "root"
DB_PASSWORD = ""  # Empty by default in XAMPP, or set your password
DB_NAME = "talkwithdata"  # Your new database name

# Build DB_URI
if DB_PASSWORD:
    DB_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
    DB_URI = f"mysql+pymysql://{DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# .env file content
env_content = f"""# Database Configuration
DB_TYPE={DB_TYPE}
DB_URI={DB_URI}

# Optional: MongoDB Configuration
# MONGO_URI=mongodb://localhost:27017/

# Optional: LLM API Keys (for query generation)
# OPENROUTER_API_KEY=your_key_here
# MISTRAL_API_KEY=your_key_here
# GENERATOR_PROVIDER=mixtral
# GENERATOR_N_CANDIDATES=5
# GENERATOR_TEMPERATURE=0.2
# GENERATOR_TOP_P=0.95
# GENERATOR_MAX_TOKENS=200

# Safety Settings
SAFETY_BLOCK_DDL=true
SAFETY_REQUIRE_WHERE=true
SELECT_LIMIT_CAP=1000
"""

# Write .env file
env_path = os.path.join(os.path.dirname(__file__), ".env")
try:
    with open(env_path, "w") as f:
        f.write(env_content)
    print(f"[SUCCESS] Created .env file at: {env_path}")
    print(f"\nConfiguration:")
    print(f"   DB_URI: {DB_URI}")
    print(f"\nPlease verify:")
    print(f"   1. MySQL is running in XAMPP")
    print(f"   2. Database '{DB_NAME}' exists")
    print(f"   3. Port {DB_PORT} is correct (check XAMPP MySQL config)")
    print(f"\nTo test connection, run: python test_mysql_connection.py")
except Exception as e:
    print(f"[ERROR] Error creating .env file: {e}")
    print(f"\n📝 Please create .env file manually with this content:")
    print("=" * 60)
    print(env_content)
    print("=" * 60)
