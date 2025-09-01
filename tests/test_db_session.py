import pytest
from app.models.db_user import User
from sqlalchemy import select


@pytest.mark.asyncio
async def test_create_and_cleanup_user(db_session):
    # Create user
    new_user = User(
        username="testuser",
        full_name="Test User",
        hashed_password="hashedpw",
        is_active=True,
        is_superuser=False,
    )
    db_session.add(new_user)
    await db_session.commit()
    await db_session.refresh(new_user)
    assert new_user.id is not None

    # Query user
    stmt = select(User).where(User.username == "testuser")
    result = await db_session.execute(stmt)
    user_obj = result.scalar_one()
    assert user_obj.full_name == "Test User"

    # Cleanup
    await db_session.delete(user_obj)
    await db_session.commit()
    # Confirm deletion
    result = await db_session.execute(select(User).where(User.username == "testuser"))
    assert result.scalar() is None
