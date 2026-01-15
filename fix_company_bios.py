#!/usr/bin/env python3

from app.db import SessionLocal
from app.models import CompanyProfile

def fix_company_bios():
    db = SessionLocal()
    try:
        # Update all company profiles to have bio = description
        profiles = db.query(CompanyProfile).filter(CompanyProfile.bio.is_(None)).all()
        print(f'Found {len(profiles)} company profiles with missing bio')
        
        for cp in profiles:
            if cp.description:
                cp.bio = cp.description
                print(f'Updated company {cp.company_name}: bio set to description')
        
        db.commit()
        print('All company profiles updated successfully!')
        
    except Exception as e:
        print(f'Error: {e}')
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_company_bios()