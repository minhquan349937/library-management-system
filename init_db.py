from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base, User, UserRole
from app.utils.auth import get_password_hash
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_users():
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Initialize Admin User
        admin = db.query(User).filter(User.email == "admin@library.com").first()
        if not admin:
            admin_user = User(
                email="admin@library.com",
                username="admin",
                hashed_password=get_password_hash("admin123"),
                role=UserRole.ADMIN,
                first_name="Admin",
                last_name="User",
                phone="+1234567890",
                address="Library Main Branch",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                is_deleted=False
            )
            db.add(admin_user)
        
        # Initialize Sample Members
        sample_members = [
            {
                "email": "john@example.com",
                "username": "johndoe",
                "first_name": "John",
                "last_name": "Doe",
                "phone": "+1987654321",
                "address": "123 Main St"
            },
            {
                "email": "jane@example.com",
                "username": "janesmith",
                "first_name": "Jane",
                "last_name": "Smith",
                "phone": "+1122334455",
                "address": "456 Oak Ave"
            }
        ]
        
        for member_data in sample_members:
            member = db.query(User).filter(User.email == member_data["email"]).first()
            if not member:
                member_data.update({
                    "hashed_password": get_password_hash("member123"),
                    "role": UserRole.MEMBER,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc),
                    "is_deleted": False
                })
                member_user = User(**member_data)
                db.add(member_user)
        
        # Commit all changes
        db.commit()
        
        print("Users initialized successfully!")
        print("\nLogin Credentials:")
        print("-----------------")
        print("Admin:")
        print("Email: admin@library.com")
        print("Password: admin123")
        print("\nMembers:")
        for member in sample_members:
            print(f"\nEmail: {member['email']}")
            print("Password: member123")
            
    except Exception as e:
        print(f"Error initializing users: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Initializing users...")
    init_users()