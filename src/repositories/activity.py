from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Activity
from repositories.base import SQLAlchemyRepository
from typing import Optional, Any, Dict


class ActivityRepository(SQLAlchemyRepository):
    model = Activity

    async def find_all(
            self,
            session: AsyncSession,
            filters: Optional[Dict[str, Any]] = None,
            limit: Optional[int] = 50,
            offset: Optional[int] = 0
    ):
        stmt = (
            select(self.model)
            .options(
                selectinload(self.model.children)
                .selectinload(self.model.children)  # если нужна глубина 2
            )
            .limit(limit)
            .offset(offset)
        )

        res = await session.execute(stmt)
        return res.scalars().all()

    async def get_activity_subtree_ids(
        self,
        session: AsyncSession,
        root_activity_id: int,
    ) -> list[int]:
        """
        Возвращает список id: [root, child1, child2, ...]
        """
        result_ids = []
        stack = [root_activity_id]

        while stack:
            current_id = stack.pop()
            result_ids.append(current_id)

            stmt = select(Activity.id).where(Activity.parent_id == current_id)
            res = await session.execute(stmt)
            children_ids = [row[0] for row in res.all()]

            stack.extend(children_ids)

        return result_ids
