Google Cloud Study
===

# Pubsub study


```sql
SELECT 
  u.email,
  count(1) sessions
FROM 
  pubsubs.sessions s
JOIN 
  pubsubs.users u ON s.user_id = u.id
GROUP BY
  u.email
```