from abc import ABC, abstractmethod

from sqlalchemy import insert, select, update, delete, and_
from typing import Dict, Any, Optional
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions import (
    ModelAlreadyExistsException,
    ModelNoFoundException
)


class AbstractRepository(ABC):
    """
    Абстрактный репозиторий нужен чтобы при наследовании определяли его базовые методы работы с бд
    """
    model = None

    @abstractmethod
    async def add_one(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def find_one(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def find_all(self, *args, **kwargs):
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    """
    Репозиторий для работы с sqlalchemy
    """
    model = None

    async def add_one(self, session: AsyncSession, data: dict):
        stmt = insert(self.model).values(**data).returning(self.model)
        try:
            res = await session.execute(stmt)
            # await session.commit()
            return res.scalar_one()
        except IntegrityError:
            raise ModelAlreadyExistsException

    async def find_all(
            self,
            session: AsyncSession,
            filters: Optional[Dict[str, Any]] = None,
            limit: Optional[int] = 50,
            offset: Optional[int] = 0
    ):
        stmt = select(self.model).limit(limit).offset(offset)

        if filters:
            # Фильтруем только те ключи, которые существуют в модели
            valid_filters = {}
            for key, value in filters.items():
                if hasattr(self.model, key) and value is not None:
                    valid_filters[key] = value

            # Создаем условия для WHERE
            if valid_filters:
                conditions = []
                for key, value in valid_filters.items():
                    conditions.append(getattr(self.model, key) == value)

                if conditions:
                    stmt = stmt.where(*conditions)

        res = await session.execute(stmt)
        return res.scalars().all()

    async def get_by_id(self, session: AsyncSession, obj_id: int):
        stmt = select(self.model).where(self.model.id == obj_id)
        try:
            res = await session.execute(stmt)
            return res.scalar_one()
        except NoResultFound:
            raise ModelNoFoundException

    async def find_one(self, session: AsyncSession, data: dict):
        stmt = select(self.model).where(**data)
        try:
            res = await session.execute(stmt)
            return res.scalar_one()
        except NoResultFound:
            raise ModelNoFoundException

    async def change_one(self, session: AsyncSession, data: dict):
        obj_id = data.pop('id')

        stmt = (
            update(self.model)
            .where(self.model.id == obj_id)
            .values(**data)
            .returning(self.model)
        )

        try:
            res = await session.execute(stmt)
            # await session.commit()
            return res.scalar_one()
        except NoResultFound:
            # await session.rollback()
            raise ModelNoFoundException
        except IntegrityError:
            # await session.rollback()
            raise ModelAlreadyExistsException


