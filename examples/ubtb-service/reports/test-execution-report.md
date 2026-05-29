# 测试执行报告

> 生成时间: 2026-05-29 16:00:18
> 目标服务: http://127.0.0.1:8080
> 测试邮箱: admin@ubtb.com

## 执行摘要

| 指标 | 数值 |
|------|------|
| 总步骤数 | 1 |
| 通过 | 0 |
| 失败 | 1 |
| 总耗时 | 39 ms |
| 平均耗时 | 39.4 ms |

## 步骤详情

### Step 1: LOGIN ❌

| 属性 | 值 |
|------|------|
| 方法 | POST |
| URL | http://127.0.0.1:8080/api/auth/login |
| HTTP 状态码 | 404 |
| 耗时 | 39.38 ms |
| 时间戳 | 2026-05-29 16:00:18 |

**请求**

Headers:
- User-Agent: python-requests/2.34.2
- Accept-Encoding: gzip, deflate, zstd
- Accept: */*
- Connection: keep-alive
- Content-Length: 49
- Content-Type: application/json

Body:
```json
{
  "email": "admin@ubtb.com",
  "password": "123456"
}
```

**响应**

Headers:
- Cache-Control: no-cache, private, no-store, must-revalidate, max-stale=0, post-check=0, pre-check=0
- Content-Encoding: gzip
- Content-Security-Policy: frame-ancestors 'self'
- Content-Type: text/html; charset=utf-8
- Date: Fri, 29 May 2026 08:00:22 GMT
- Etag: W/"48a-ZSWE2NpCdLXTjY/soSPHjuceRf8"
- Referrer-Policy: strict-origin-when-cross-origin
- Strict-Transport-Security: max-age=31536000;
- Vary: Accept-Encoding
- Via: 1.1 Caddy
- X-Content-Type-Options: nosniff
- X-Powered-By: Express
- X-Xss-Protection: 1; mode=block
- Transfer-Encoding: chunked

Body:
```json
{
  "raw": "<!DOCTYPE html>\n<html class=\"no-js\" lang=\"en\">\n  <head>\n    <meta charset=\"UTF-8\" />\n\n    <title>404 — Page not found</title>\n\n    <meta name=\"viewport\" content=\"user-scalable=no, width=device-width, initial-scale=1, maximum-scale=1\">\n    <meta name=\"mobile-web-app-capable\" content=\"yes\" />\n    <meta name=\"apple-mobile-web-app-capable\" content=\"yes\" />\n\n    <link rel=\"stylesheet\" href=\"/public/ghost.min.css?v=f190998318\"/>\n\n  </head>\n  <body>\n    <main role=\"main\" id=\"main\">\n      <div class=\"gh"
}
```

**验证点**

- HTTP 状态码检查: ❌ 失败
- 业务码检查: ❌ 失败
- 额外检查项:
  - HTTP status 404 not in expected (200,)

---

*本报告由 core-flow 测试脚本自动生成*