'''Step 4 — Build the loader
In loaders/prices.py, save the cleaned records to PostgreSQL.
You'll need to:
- Establish a database connection.
- Insert the records into your price-history table.
- Use a unique constraint on the asset and timestamp.
- Use an upsert or equivalent strategy to make reruns safe.
- Handle database errors without silently losing data.
You can build this after defining your database schema in database/.'''