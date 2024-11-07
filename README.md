Google Cloud Study
===

# Pubsub study


```sql
SELECT 
  m.movie,
  count(1) sessions
FROM 
  pubsubs.sessions s
JOIN  
  pubsubs.movies m ON m.movie = s.movie
GROUP BY m.movie
```