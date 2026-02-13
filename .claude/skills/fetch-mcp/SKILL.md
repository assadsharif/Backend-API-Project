---
name: fetch-mcp
description: Web content fetching using the Fetch MCP server. Use when Claude needs to access web content, documentation, API references, or public data from URLs. Triggers on requests to fetch, retrieve, or access content from websites, documentation sites, or public APIs.
---

# Fetch MCP

Web content fetching using the @modelcontextprotocol/server-fetch MCP server.

## Overview

Fetch and process web content from public URLs. Access documentation, API references, and online resources during development.

## Core Capabilities

### 1. Fetch Web Pages
```
"Fetch the FastAPI documentation homepage"
"Get content from this URL: https://example.com"
```
→ Use `fetch` for general web content

### 2. Fetch HTML
```
"Fetch and parse this HTML page"
"Extract links from this webpage"
```
→ Use `fetch_html` for HTML parsing

### 3. Fetch JSON
```
"Fetch this API endpoint: https://api.example.com/data"
"Get JSON from this URL"
```
→ Use `fetch_json` for JSON APIs

### 4. Fetch Text
```
"Get the raw text from this documentation"
"Fetch plain text content"
```
→ Use `fetch_text` for plain text

## Workflow Decision Tree

```
Web fetch request
│
├─ HTML page? → fetch_html
├─ JSON API? → fetch_json
├─ Plain text? → fetch_text
├─ General content? → fetch
└─ Extract specific data? → fetch + parse
```

## Common Use Cases

### 1. Documentation Access
```
"Fetch the FastAPI security documentation"
"Get the Next.js data fetching guide"
"Access the SQLModel ORM docs"
```

### 2. API Research
```
"Fetch the OpenAI API reference for chat completions"
"Get the Vercel deployment API docs"
"Access the GitHub API documentation"
```

### 3. Package Information
```
"Fetch package.json from the FastAPI repo"
"Get the latest version info for @anthropic/sdk"
```

### 4. Community Resources
```
"Fetch this tutorial: [URL]"
"Get this blog post about best practices"
```

## Common Patterns

### Pattern 1: Research Before Implementation
```
1. Identify need for external info
2. Fetch official documentation → fetch_html(docs_url)
3. Extract relevant sections
4. Apply to implementation
```

### Pattern 2: API Integration Research
```
1. Fetch API documentation → fetch_html(api_docs_url)
2. Fetch API schema → fetch_json(schema_url)
3. Understand endpoints and parameters
4. Implement integration
```

### Pattern 3: Version Verification
```
1. Fetch package info → fetch_json(package_url)
2. Check latest version
3. Verify compatibility
4. Update dependencies
```

## Integration with Development Workflow

**During spec phase:**
```
Fetch documentation to validate feature feasibility
```

**During implementation:**
```
Access API references for correct usage
```

**During troubleshooting:**
```
Fetch error documentation or solutions
```

## Limitations

### ❌ Cannot Fetch
- Authenticated content (login required)
- Private networks (localhost, 192.168.x.x)
- Content behind CORS restrictions
- Very large files (>10MB typically)
- JavaScript-rendered content (needs static HTML)

### ✅ Can Fetch
- Public documentation sites
- Public API endpoints
- Open-source repository files
- Public JSON data
- Static web pages

## Best Practices

### ✅ DO
- Fetch from official documentation sources
- Use stable, versioned URLs
- Cache mental notes of fetched content
- Verify URL is publicly accessible
- Respect rate limits

### ❌ DON'T
- Fetch from localhost
- Spam the same URL repeatedly
- Fetch extremely large files
- Assume JavaScript will execute
- Fetch from private networks

## Common URLs

**Framework Documentation:**
- FastAPI: https://fastapi.tiangolo.com
- Next.js: https://nextjs.org/docs
- SQLModel: https://sqlmodel.tiangolo.com

**API References:**
- OpenAI: https://platform.openai.com/docs
- GitHub: https://docs.github.com/rest
- Vercel: https://vercel.com/docs/rest-api

**Package Repositories:**
- npm: https://registry.npmjs.org/<package>
- PyPI: https://pypi.org/pypi/<package>/json
- GitHub: https://api.github.com/repos/<owner>/<repo>

## Reference

For detailed documentation:
- [Fetch MCP README](../../mcp/fetch/README.md)
- [MCP Installation Summary](../../mcp/INSTALLATION_SUMMARY.md)
