from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.task import Task, TaskCreate, TaskUpdate

class TaskRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_task(self, task_create: TaskCreate, owner_id: int) -> Task:
        new_task = Task(
            title=task_create.title,
            description=task_create.description,
            completed=task_create.completed or False,
            owner_id=owner_id
        )
        self.db.add(new_task)
        await self.db.commit()
        await self.db.refresh(new_task)
        return new_task

    async def get_tasks_by_user(self, user_id: int):
        result = await self.db.execute(select(Task).where(Task.owner_id == user_id))
        return result.scalars().all()

    async def get_task_by_id(self, task_id: int):
        result = await self.db.execute(select(Task).where(Task.id == task_id))
        return result.scalars().first()

    async def update_task(self, task: Task, task_update: TaskUpdate):
        if task_update.title is not None:
            task.title = task_update.title
        if task_update.description is not None:
            task.description = task_update.description
        if task_update.completed is not None:
            task.completed = task_update.completed
        
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def delete_task(self, task: Task):
        await self.db.delete(task)
        await self.db.commit()
