#!/usr/bin/env python3

from app.db import SessionLocal
from app.models import User, CompanyProfile, UserRole

def debug_companies():
    db = SessionLocal()
    try:
        companies = db.query(User).filter(User.role == UserRole.COMPANY).all()
        print(f'Found {len(companies)} companies:')
        
        for c in companies[:3]:  # First 3 companies
            print(f'\nCompany {c.id}:')
            print(f'  username: {c.username}')
            print(f'  name: {c.name}')
            print(f'  surname: {c.surname}')
            print(f'  profile_image_url: {c.profile_image_url}')
            
            cp = db.query(CompanyProfile).filter(CompanyProfile.user_id == c.id).first()
            if cp:
                print(f'  CompanyProfile found:')
                print(f'    company_name: {cp.company_name}')
                print(f'    industry: {cp.industry}')
                print(f'    bio: {cp.bio}')
                print(f'    description: {cp.description}')
                print(f'    website: {cp.website}')
            else:
                print(f'  No CompanyProfile found!')
        
    finally:
        db.close()

if __name__ == "__main__":
    debug_companies()