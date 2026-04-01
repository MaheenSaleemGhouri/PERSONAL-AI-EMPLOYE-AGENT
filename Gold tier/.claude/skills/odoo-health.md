# odoo-health

Check if the Odoo instance is running and reachable.

## Arguments

```
/odoo-health
```

## Instructions

When invoked:

1. **Connect to Odoo** using `watchers/odoo_connector.py`.
2. Call `client.health_check()`.
3. Report the status:
   - If OK: display version info and confirm connectivity.
   - If error: display the error and suggest checking Docker (`docker compose ps` in the `odoo/` directory).
4. Optionally check Docker container status via `docker compose -f odoo/docker-compose.yml ps`.
5. **Log** to `/Logs/YYYY-MM-DD.md`.

## Rules

- This is a diagnostic skill — read-only, no side effects.
