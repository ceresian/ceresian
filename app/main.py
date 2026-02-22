from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .config import get_settings
from .db import get_conn, init_db
from .services import cosine_similarity, to_user_rating_map, weighted_critic_score
from .tmdb import TMDBClient

app = FastAPI(title=get_settings().app_name)


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    is_critic: bool = False


class ReviewCreate(BaseModel):
    user_id: int
    tmdb_movie_id: int
    rating: float = Field(ge=0, le=10)
    review_text: str = ""


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/users")
def create_user(payload: UserCreate) -> dict:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO users(name, is_critic) VALUES (?, ?)",
            (payload.name, int(payload.is_critic)),
        )
        return {"id": cur.lastrowid, **payload.model_dump()}


@app.post("/reviews")
def upsert_review(payload: ReviewCreate) -> dict:
    with get_conn() as conn:
        exists = conn.execute(
            "SELECT id FROM users WHERE id = ?", (payload.user_id,)
        ).fetchone()
        if not exists:
            raise HTTPException(status_code=404, detail="User not found")

        conn.execute(
            """
            INSERT INTO movie_reviews(user_id, tmdb_movie_id, rating, review_text)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, tmdb_movie_id)
            DO UPDATE SET rating = excluded.rating, review_text = excluded.review_text
            """,
            (
                payload.user_id,
                payload.tmdb_movie_id,
                payload.rating,
                payload.review_text,
            ),
        )
    return {"ok": True}


@app.get("/movies/search")
async def search_movies(q: str) -> list[dict]:
    client = TMDBClient()
    return await client.search_movies(q)


@app.get("/movies/{tmdb_movie_id}/aggregate")
def aggregate_movie(tmdb_movie_id: int, user_id: int) -> dict:
    with get_conn() as conn:
        users = conn.execute("SELECT id, is_critic FROM users").fetchall()
        if not users:
            raise HTTPException(status_code=404, detail="No users found")

        reviews = conn.execute(
            "SELECT user_id, tmdb_movie_id, rating FROM movie_reviews"
        ).fetchall()
        ratings_map = to_user_rating_map(reviews)

        if user_id not in ratings_map:
            raise HTTPException(
                status_code=400,
                detail="User has no ratings yet. Add a few reviews to compute critic matching.",
            )

        target = ratings_map[user_id]
        critics = [row["id"] for row in users if row["is_critic"] == 1 and row["id"] != user_id]

        critic_weighted_reviews = []
        matched_critics = []

        for critic_id in critics:
            critic_ratings = ratings_map.get(critic_id, {})
            similarity = cosine_similarity(target, critic_ratings)
            if tmdb_movie_id in critic_ratings:
                critic_weighted_reviews.append((similarity, critic_ratings[tmdb_movie_id]))
            if similarity > 0:
                matched_critics.append(
                    {
                        "critic_id": critic_id,
                        "similarity": round(similarity, 3),
                    }
                )

        aggregate = weighted_critic_score(critic_weighted_reviews)
        return {
            "tmdb_movie_id": tmdb_movie_id,
            "user_id": user_id,
            "aggregate_score": aggregate,
            "matched_critics": sorted(
                matched_critics, key=lambda x: x["similarity"], reverse=True
            )[:10],
        }
