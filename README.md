Steps:

1. create docker-compose.yml with the following content.

```yaml
version: '3.8'

services:
  ts-db:
    image: timescale/timescaledb-ha:pg16 # pgai only available for ha and pg16+
    container_name: ts-db
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: tsuser
      POSTGRES_PASSWORD: tspassword
      POSTGRES_DB: ts-db
      POSTGRES_MAX_WAL_SIZE: 4GB
      POSTGRES_CHECKPOINT_TIMEOUT: 15min
      POSTGRES_CHECKPOINT_COMPLETION_TARGET: 0.9
    volumes:
      - ~/timescale_data:/var/lib/postgresql/data

volumes:
  timescale_data:
  ollama:
networks:
  ollama_net:
    driver: bridge
```
2. Start timescale db container
3. Run `create extension if not exists ai cascade;`
4. Download and install ollama in local (not a docker container).
5. Run `ollama run llama3:8b` and wait until the model is pulled and olla server is running.
6. Create a table with the following schema and insert some data:

```sql
create table instruments_embed
(
    created_at     timestamp without time zone,
    org_id     integer,
    instrument_id  uuid,
    instrument_type text,
    embedding  vector(4096)
);

INSERT INTO instruments_embed (created_at, org_id, instrument_id, instrument_type) VALUES
('2024-08-14 13:59:02', 1, 'f47ac10b-58cc-4372-a567-0e02b2c3d479', 'guitar'),
('2024-08-14 14:00:02', 2, 'f47ac10b-58cc-4372-a567-0e02b2c3d470', 'piano'),
('2024-08-14 14:01:02', 3, 'f47ac10b-58cc-4372-a567-0e02b2c3d471', 'violin'),
('2024-08-14 14:02:02', 4, 'f47ac10b-58cc-4372-a567-0e02b2c3d472', 'drums'),
('2024-08-14 14:03:02', 5, 'f47ac10b-58cc-4372-a567-0e02b2c3d473', 'flute'),
('2024-08-14 14:04:02', 6, 'f47ac10b-58cc-4372-a567-0e02b2c3d474', 'trumpet'),
('2024-08-14 14:05:02', 7, 'f47ac10b-58cc-4372-a567-0e02b2c3d475', 'saxophone'),
('2024-08-14 14:06:02', 8, 'f47ac10b-58cc-4372-a567-0e02b2c3d476', 'clarinet'),
('2024-08-14 14:07:02', 9, 'f47ac10b-58cc-4372-a567-0e02b2c3d477', 'tuba'),
('2024-08-14 14:08:02', 10, 'f47ac10b-58cc-4372-a567-0e02b2c3d478', 'harp');


update instruments_embed set embedding = ollama_embed('llama3.1', format('%s - %s - %s - %s', created_at, org_id, instrument_id, instrument_type), 'http://host.docker.internal:host-gateway:11434');
```

Problem: `update` statement takes 5-6 seconds to update a single row. We need to optimize this. Feel free to change the configurations or steps to implement.

## Proposed solution
The ollama_embed() function for generating the embedding seems to be the reason for the slow execution of the `update` statement.

The number of vector dimensions affect the speed of the update query
I used a different embedding model `nomic-embed-text` which creates embeddings with 768 dimensions. That is:
```sql
update instruments_embed set embedding = ollama_embed('nomic-embed-text', format('%s - %s - %s - %s', created_at, org_id, instrument_id, instrument_type), 'http://host.docker.internal:host-gateway:11434');
```

NOTE: This requires the Table to be defined as follows:
```sql
create table instruments_embed
(
    created_at     timestamp without time zone,
    org_id     integer,
    instrument_id  uuid,
    instrument_type text,
    embedding  vector(768)
);
```

