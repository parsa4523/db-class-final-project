from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from ..database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

    # Relationships
    apps = relationship("App", back_populates="category")
