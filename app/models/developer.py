from sqlalchemy import Column, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from ..database import Base

class Developer(Base):
    __tablename__ = "developers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    website = Column(String(500))
    email = Column(String(255))

    # Relationships
    apps = relationship("App", back_populates="developer")

    # Enforce unique constraint on name and email combination
    __table_args__ = (
        UniqueConstraint('name', 'email', name='developers_name_email_key'),
    )
