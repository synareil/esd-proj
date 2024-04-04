INSERT INTO "user" (id, email, name) VALUES (1, 'youremail@example.com', 'yourname')
ON CONFLICT (id) DO UPDATE SET email = EXCLUDED.email, name = EXCLUDED.name;