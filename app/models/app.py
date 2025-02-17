from sqlalchemy import (
    Column, Integer, String, ForeignKey, 
    Numeric, Date, DateTime, Boolean, Text,
    Index
)
from sqlalchemy.orm import relationship

from ..database import Base

class App(Base):
    __tablename__ = "apps"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    app_id = Column(String(255), unique=True, nullable=False)
    
    # Foreign keys
    category_id = Column(Integer, ForeignKey('categories.id'))
    developer_id = Column(Integer, ForeignKey('developers.id'))
    
    # Metrics
    rating = Column(Numeric(2, 1))
    rating_count = Column(Integer)
    installs = Column(String(50))
    min_installs = Column(Integer)
    max_installs = Column(Integer)
    
    # Pricing
    is_free = Column(Boolean)
    price = Column(Numeric(10, 2))
    currency = Column(String(3))
    
    # Technical details
    size = Column(String(20))
    min_android = Column(String(50))
    
    # Dates
    released_date = Column(Date)
    last_updated = Column(Date)
    
    # Content info
    content_rating = Column(String(50))
    privacy_policy_url = Column(Text)
    
    # Features
    has_ads = Column(Boolean)
    has_in_app_purchases = Column(Boolean)
    is_editors_choice = Column(Boolean)
    
    # Metadata
    scraped_time = Column(DateTime)
    
    # Relationships
    category = relationship("Category", back_populates="apps")
    developer = relationship("Developer", back_populates="apps")

    # Table arguments including indexes
    __table_args__ = (
        Index('idx_apps_category_cover', 
              'category_id', 
              'rating', 
              'last_updated',
              postgresql_include=['name', 'app_id', 'is_free', 'rating_count', 
                                'has_ads', 'is_editors_choice', 'released_date']
        ),
        Index('idx_apps_category_rating',
              'category_id',
              'rating'),
        Index('idx_apps_yearly_stats',
              'category_id',
              'released_date',
              'last_updated'),
    )
