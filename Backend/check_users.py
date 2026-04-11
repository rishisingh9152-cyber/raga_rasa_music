
import asyncio
from app.database import get_db, init_db

async def check_users():
    await init_db()
    db = get_db()
    users = await db.users.find().to_list(length=100)
    print(f"Total users: {len(users)}")
    for user in users:
        print(f"User: {user.get('email')}, Role: {user.get('role')}, ID: {user.get('user_id')}")

if __name__ == "__main__":
    asyncio.run(check_users())
