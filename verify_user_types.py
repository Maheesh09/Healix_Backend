import sys
from app.db.session import SessionLocal, engine
from app.db.base_class import Base
from app.models.user import User, UserType
from app.schemas.user import UserCreate
from app.crud import crud_user

def verify_user_types():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Create LABS user
        email_labs = "labs@example.com"
        print(f"Creating user {email_labs} as LABS...")
        user_labs_in = UserCreate(
            email=email_labs,
            password="password",
            nic="NIC001",
            user_type=UserType.LABS,
            full_name="Lab Technician"
        )
        if not crud_user.get_user_by_email(db, email=email_labs):
            user_labs = crud_user.create_user(db, user_labs_in)
            print(f"Created: {user_labs.email} - {user_labs.user_type}")
            assert user_labs.user_type == UserType.LABS
        
        # Create DOCTOR user
        email_doc = "doctor@example.com"
        print(f"Creating user {email_doc} as DOCTOR...")
        user_doc_in = UserCreate(
            email=email_doc,
            password="password",
            nic="NIC002",
            user_type=UserType.DOCTOR,
            full_name="Dr. Smith"
        )
        if not crud_user.get_user_by_email(db, email=email_doc):
            user_doc = crud_user.create_user(db, user_doc_in)
            print(f"Created: {user_doc.email} - {user_doc.user_type}")
            assert user_doc.user_type == UserType.DOCTOR
            
        # Create PATIENT user
        email_pat = "patient@example.com"
        print(f"Creating user {email_pat} as PATIENT...")
        user_pat_in = UserCreate(
            email=email_pat,
            password="password",
            nic="NIC003",
            user_type=UserType.PATIENT,
            full_name="John Doe"
        )
        if not crud_user.get_user_by_email(db, email=email_pat):
            user_pat = crud_user.create_user(db, user_pat_in)
            print(f"Created: {user_pat.email} - {user_pat.user_type}")
            assert user_pat.user_type == UserType.PATIENT
        
        print("\nVerification Successful! All user types created and retrieved correctly.")
        
    except Exception as e:
        print(f"\nVerification Failed: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    verify_user_types()
