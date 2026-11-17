"""Account ownership is enforced server-side, including for administrators."""
from fastapi import HTTPException


async def claim_session(db, session_id: str, user_id: str) -> None:
    async with db.execute("SELECT owner_id FROM inbox_items WHERE session_id = ?", (session_id,)) as cur:
        saved = await cur.fetchone()
    if saved is not None and saved[0] != user_id:
        raise HTTPException(404, "Visit not found in your account.")
    await db.execute(
        "INSERT OR IGNORE INTO session_owners (session_id, user_id) VALUES (?, ?)",
        (session_id, user_id),
    )
    async with db.execute("SELECT user_id FROM session_owners WHERE session_id = ?", (session_id,)) as cur:
        owner = await cur.fetchone()
    if owner is None or owner[0] != user_id:
        await db.rollback()
        raise HTTPException(404, "Visit not found in your account.")
    await db.commit()
