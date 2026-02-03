from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table, ARRAY
from sqlalchemy.orm import relationship, declarative_base, validates
from exceptions import ActivityValidationError
from db.database import Base

# Таблица для связи многие-ко-многим между Организациями и Деятельностями
organization_activity = Table(
    'organization_activity',
    Base.metadata,
    Column('organization_id', Integer, ForeignKey('organizations.id')),
    Column('activity_id', Integer, ForeignKey('activities.id'))
)


class Building(Base):
    """Модель Здания"""
    __tablename__ = 'buildings'

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String(500), nullable=False, unique=True)
    latitude = Column(Float, nullable=False)  # Широта
    longitude = Column(Float, nullable=False)  # Долгота

    # Связь с организациями
    organizations = relationship("Organization", back_populates="building", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Building {self.address}>"


class Activity(Base):
    """Модель Деятельности с поддержкой древовидной структуры"""
    __tablename__ = 'activities'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    level = Column(Integer, default=1)  # Уровень вложенности
    parent_id = Column(Integer, ForeignKey('activities.id'), nullable=True)

    @validates('level')
    def validate_level(self, key, level):
        """Валидация уровня - максимум 3"""
        if level > 3:
            raise ActivityValidationError("Уровень активности не может быть больше 3")
        return level

    @validates('parent_id')
    def validate_parent(self, key, parent_id):
        """Валидация родителя для контроля вложенности"""
        if parent_id:
            # Проверяем, что родитель не имеет уровень 3
            from sqlalchemy.orm import Session
            session = Session.object_session(self)
            if session:
                parent = session.query(Activity).get(parent_id)
                if parent and parent.level >= 3:
                    raise ActivityValidationError("Нельзя создать дочернюю активность для уровня 3")
        return parent_id

    # Рекурсивная связь для древовидной структуры
    parent = relationship(
        "Activity",
        remote_side=[id],
        back_populates="children",
        lazy="select"  # Добавить эту строку
    )
    children = relationship(
        "Activity",
        back_populates="parent",
        cascade="all, delete-orphan",
        lazy="select"  # Добавить эту строку
    )

    # Связь с организациями
    organizations = relationship(
        "Organization",
        secondary=organization_activity,
        back_populates="activities"
    )

    def __repr__(self):
        return f"<Activity {self.name} (Level: {self.level})>"


class Organization(Base):
    """Модель Организации"""
    __tablename__ = 'organizations'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(300), nullable=False)
    building_id = Column(Integer, ForeignKey('buildings.id'), nullable=False)
    phone_numbers = Column(ARRAY(String), nullable=False, default=[])  # Массив телефонов

    # Связи
    building = relationship(
        "Building",
        back_populates="organizations",
        lazy="selectin"
    )

    activities = relationship(
        "Activity",
        secondary=organization_activity,
        back_populates="organizations",
        lazy="selectin"
    )

    def __repr__(self):
        return f"<Organization {self.name}>"
