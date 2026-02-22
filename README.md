# Critic Compass

A starter API for a movie-discovery app that helps users find critics whose taste aligns with their own ratings, then computes a personalized aggregate score for movies.

## Why this approach

- **TMDB-first integration** for movie search and metadata.
- **No paid Rotten Tomatoes dependency** right now.
- **Taste matching** via critic similarity based on shared rating history.
- **User reviews** included from day one.

## MVP features implemented

- Create users (regular users or critics)
- Add/update movie reviews by TMDB movie ID
- Search movies from TMDB (`/movies/search`)
- Compute personalized aggregate scores from matched critics (`/movies/{tmdb_movie_id}/aggregate`)

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Open docs at: `http://127.0.0.1:8000/docs`

## API flow for your product idea

1. User searches movie with TMDB
2. User rates/reviews movies they have seen
3. Critics also rate/review movies
4. API calculates critic-user similarity
5. API returns personalized aggregate score and top matching critics

## Next steps (recommended)

- Add authentication (JWT + social login)
- Save TMDB movie metadata locally for caching/performance
- Add "follow critic" graph and recommendation feed
- Add content-based and collaborative filtering recommendations
- Optional Rotten Tomatoes scraping/import pipeline later (when legal/business constraints are clear)

## Data model

- `users(id, name, is_critic)`
- `movie_reviews(id, user_id, tmdb_movie_id, rating, review_text, created_at)`

## Notes

- If `TMDB_API_KEY` is missing, `/movies/search` returns an empty array.
- Aggregate score uses weighted average of critic ratings by cosine similarity.
