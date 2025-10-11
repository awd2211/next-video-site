# API测试问题报告

## 总结

- 总端点: 103
- 通过: 44
- 500错误: 11
- 认证问题: 0

## 500错误（需要立即修复）

- `GET /api/v1/categories`
  ```
  {"detail":"Internal server error"}
  ```

- `GET /api/v1/notifications/`
  ```
  {"detail":"Internal server error"}
  ```

- `GET /api/v1/notifications/stats`
  ```
  {"detail":"Internal server error"}
  ```

- `POST /api/v1/notifications/mark-all-read`
  ```
  {"detail":"Internal server error"}
  ```

- `POST /api/v1/notifications/clear-all`
  ```
  {"detail":"Internal server error"}
  ```

- `GET /api/v1/recommendations/for-you`
  ```
  {"detail":"Internal server error"}
  ```

- `GET /api/v1/users/me/favorites`
  ```
  {"detail":"Internal server error"}
  ```

- `GET /api/v1/videos/trending`
  ```
  {"detail":"Internal server error"}
  ```

- `GET /api/v1/videos/featured`
  ```
  {"detail":"Internal server error"}
  ```

- `GET /api/v1/videos/recommended`
  ```
  {"detail":"Internal server error"}
  ```

- `GET /api/v1/admin/videos`
  ```
  {"detail":"Internal server error"}
  ```

