# API Reference

Interactive documentation:
https://digital-banking-backend-gctw.onrender.com/docs

Live API:
https://digital-banking-backend-gctw.onrender.com

Health check:
https://digital-banking-backend-gctw.onrender.com/health

| Method | Endpoint | Summary | Tags |
|---|---|---|---|
| `GET` | `/` | Root | General |
| `GET` | `/accounts` | Get My Accounts | Accounts |
| `POST` | `/accounts` | Create Account | Accounts |
| `GET` | `/accounts/{account_id}` | Get My Account | Accounts |
| `PATCH` | `/accounts/{account_id}` | Update My Account | Accounts |
| `POST` | `/accounts/{account_id}/deposit` | Deposit | Accounts |
| `GET` | `/accounts/{account_id}/transactions` | Get Account Transactions | Accounts |
| `POST` | `/accounts/{account_id}/withdraw` | Withdraw | Accounts |
| `POST` | `/accounts/{source_account_id}/transfer` | Transfer | Accounts |
| `POST` | `/auth/login` | Login | Authentication |
| `GET` | `/auth/me` | Get My Profile | Authentication |
| `GET` | `/users` | Get All Users | Users |
| `POST` | `/users` | Create User | Users |
| `DELETE` | `/users/{user_id}` | Delete User | Users |
| `GET` | `/users/{user_id}` | Get User | Users |
| `PATCH` | `/users/{user_id}` | Update User | Users |
| `GET` | `/health` | Database connectivity health check | Health |

## Authentication

Protected endpoints use the configured authentication dependencies. Authenticate through the login endpoint and use the returned access token in the Swagger Authorize dialog.

## Common Response Codes

| Status | Meaning |
|---|---|
| 200 | Successful request |
| 201 | Resource created or transaction completed |
| 401 | Authentication required or invalid |
| 403 | Insufficient privileges |
| 404 | Resource not found or inaccessible |
| 409 | Resource or idempotency conflict |
| 422 | Request validation failed |
| 500 | Unexpected server error |
