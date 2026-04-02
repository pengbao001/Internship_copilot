from app.db.session import SessionFactory
from app.models.internship import Internship
from app.models.profile import Profile
from sqlalchemy import select

# Insertion
"""
with SessionFactory.begin() as session:
    profile = Profile(
        full_name='Bob',
        email='bob@gmail.com',
        github_url='https://github.com/bob',
        linkedin_url='https://www.linkedin.com/in/bob/',
        resume_text="Python, machine learning, PyTorch, NLP",
        summary="Interested in AI research internships."
    )
    session.add(profile)

with SessionFactory.begin() as session:
    internship = Internship(
        title='AI Internship',
        company_name='Open Research Lab',
        location='Remote',
        source_url='https://example.com/internship_001',
        raw_description="Looking for Python, PyTorch, NLP, and SQL experience.",
        cleaned_description="Looking for Python, PyTorch, NLP, and SQL experience.",
        is_active=True,
    )
    session.add(internship)
"""

with SessionFactory() as session:
    profiles = session.scalars(select(Profile)).all()
    print(profiles)

with SessionFactory() as session:
    internships = session.scalars(select(Internship)).all()
    print(internships)

with SessionFactory() as session:
    rows = session.execute(
        select(Internship.title, Internship.company_name)
    ).all()
    print(rows)

with SessionFactory() as session:
    remote_roles = session.scalars(
        select(Internship).where(Internship.location == 'Remote')
    ).all()
    print(remote_roles)
