from typing import Generic, TypeVar, Type, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, asc
from sqlalchemy.orm import DeclarativeBase

ModelType = TypeVar("ModelType", bound=DeclarativeBase)
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations."""

    def __init__(self, db: AsyncSession, model: Type[ModelType]):
        self.db = db
        self.model = model

    async def get(self, id: any) -> Optional[ModelType]:
        """Get a single record by ID."""
        statement = select(self.model).where(self.model.id == id)
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None,
        order_desc: bool = False,
        filters: Optional[dict] = None,
    ) -> tuple[List[ModelType], int]:
        """Get multiple records with pagination and filtering."""
        statement = select(self.model)

        # Apply filters if provided
        if filters:
            for field_name, value in filters.items():
                if hasattr(self.model, field_name):
                    statement = statement.where(
                        getattr(self.model, field_name) == value
                    )

        # Get total count
        count_statement = select(func.count()).select_from(self.model)
        if filters:
            for field_name, value in filters.items():
                if hasattr(self.model, field_name):
                    count_statement = count_statement.where(
                        getattr(self.model, field_name) == value
                    )
        total = await self.db.execute(count_statement)
        count = total.scalar()

        # Apply sorting
        if order_by and hasattr(self.model, order_by):
            field = getattr(self.model, order_by)
            if order_desc:
                statement = statement.order_by(desc(field))
            else:
                statement = statement.order_by(asc(field))

        # Apply pagination
        statement = statement.offset(skip).limit(limit)

        result = await self.db.execute(statement)
        return result.scalars().all(), count

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record."""
        db_obj = self.model(**obj_in.model_dump())
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(
        self, db_obj: ModelType, obj_in: UpdateSchemaType
    ) -> ModelType:
        """Update an existing record."""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, db_obj: ModelType) -> ModelType:
        """Delete a record."""
        await self.db.delete(db_obj)
        await self.db.commit()
        return db_obj

    async def delete_by_id(self, id: any) -> bool:
        """Delete a record by ID."""
        db_obj = await self.get(id)
        if not db_obj:
            return False
        await self.db.delete(db_obj)
        await self.db.commit()
        return True
