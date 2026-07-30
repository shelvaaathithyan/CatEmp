from typing import Optional, List
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.site import Site
from app.schemas.site import SiteCreate, SiteBase

class SiteRepository(BaseRepository[Site, SiteCreate, SiteBase]):
    def get_all(self, db: Session, skip: int = 0, limit: int = 100, customer_id: Optional[int] = None) -> List[Site]:
        """Fetch sites with optional customer filtering."""
        query = db.query(self.model)
        if customer_id:
            query = query.filter(self.model.customer_id == customer_id)
        return query.offset(skip).limit(limit).all()

site_repo = SiteRepository(Site)
