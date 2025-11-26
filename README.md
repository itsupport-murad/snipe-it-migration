# Snipe-IT Migration Helper

This container helps migrate your Snipe-IT backup into a Coolify deployment.

## How to Use

### 1. Deploy to Coolify

1. Push this repo to GitHub
2. In Coolify, create a new **Docker** resource from this repo
3. Set these environment variables:
   - `DB_HOST=i8ko4k0o48w0kosssoggsg8s`
   - `DB_PORT=3306`
   - `DB_DATABASE=default`
   - `DB_USERNAME=mariadb`
   - `DB_PASSWORD=JWZC24kSc3CaNLjRR6i7fNQOCJImYAUSt3USomIOJeJNZwp6f1zhn8NH0i387BCm`

4. Deploy the container

### 2. Run the Migration

Open the **Terminal** in Coolify for this container and run:

```bash
python migrate.py
```

### 3. Done!

After the migration completes, your Snipe-IT instance will have all your old data.
