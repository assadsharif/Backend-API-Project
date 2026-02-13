# Fetch MCP Server

Official Model Context Protocol server for web content fetching.

## 📋 Overview

The Fetch MCP server provides Claude with the ability to fetch and process web content. This enables your Digital FTE to access documentation, APIs, and other web resources during development.

## 🔌 Installation Status

✅ **Installed and Configured**

- **Type:** stdio MCP Server
- **Package:** `@modelcontextprotocol/server-fetch`
- **Status:** Active

## 🛠️ Available Tools

### Web Fetching
- **fetch** - Fetch content from a URL
- **fetch_html** - Fetch and parse HTML content
- **fetch_json** - Fetch and parse JSON data
- **fetch_text** - Fetch plain text content

### Content Processing
- **extract_links** - Extract all links from a webpage
- **extract_metadata** - Extract page metadata (title, description, etc.)
- **extract_structured_data** - Extract structured data (JSON-LD, microdata)

## 💡 Example Usage

### Fetch Documentation
```
"Fetch the FastAPI documentation for database connections"
"Get the latest Next.js documentation on server components"
"Fetch the SQLModel ORM guide from the official docs"
```

### API Research
```
"Fetch the Neon database API documentation"
"Get the OpenAI API reference for chat completions"
"Fetch the Vercel deployment API docs"
```

### Web Content Analysis
```
"Fetch this article and summarize it: [URL]"
"Extract all links from the Python Package Index for FastAPI"
"Get the metadata from this webpage"
```

### JSON Data Fetching
```
"Fetch this JSON API endpoint: [URL]"
"Get the package.json from the Next.js GitHub repo"
```

## 🔐 Security & Limitations

### Security Features
- **URL Validation** - Only fetches from valid HTTP/HTTPS URLs
- **Content Type Checking** - Validates response content types
- **Size Limits** - Prevents fetching extremely large files
- **Timeout Protection** - Requests timeout after reasonable duration

### Limitations
- No authentication support (public URLs only)
- Cannot bypass CORS restrictions
- Cannot fetch from localhost or private IPs
- Subject to rate limiting by target servers

## 🔧 Configuration

The Fetch MCP server is configured in `~/.claude.json`:

```json
{
  "fetch": {
    "type": "stdio",
    "command": "npx",
    "args": [
      "@modelcontextprotocol/server-fetch"
    ],
    "env": {}
  }
}
```

### Optional: Custom User Agent

To set a custom user agent:

```bash
claude mcp remove fetch -s local
claude mcp add fetch -e USER_AGENT="MyBot/1.0" -- npx @modelcontextprotocol/server-fetch
```

## 🎯 Use Cases for Digital FTE

### Documentation Access
- Fetch official framework documentation
- Access API references
- Get library usage examples
- Retrieve changelog information

### Research & Learning
- Research best practices
- Learn new technologies
- Find code examples
- Access tutorials

### API Integration
- Fetch API schemas
- Get API documentation
- Retrieve sample responses
- Access API versioning info

### Content Aggregation
- Collect relevant articles
- Aggregate documentation
- Fetch release notes
- Get community resources

## 🚀 Quick Start

### Test Fetching
Ask Claude:
```
"Fetch https://httpbin.org/get and show me the response"
```

### Fetch Documentation
```
"Fetch the FastAPI homepage and summarize it"
```

### Fetch JSON
```
"Fetch https://api.github.com/repos/anthropics/anthropic-sdk-python"
```

## 📊 Server Status

Check server status:
```bash
claude mcp list
# Should show: fetch - ✓ Connected
```

Get server details:
```bash
claude mcp get fetch
```

## 🔄 Integration with Development Workflow

### Documentation-Driven Development
- Fetch official docs during implementation
- Reference API documentation
- Get library examples

### Spec Enhancement
- Research features from documentation
- Validate API capabilities
- Get accurate technical details

### Learning & Adaptation
- Fetch best practices
- Learn from examples
- Stay updated with latest docs

### Quality Assurance
- Verify API endpoints
- Check documentation accuracy
- Validate integration approaches

## 🆚 Fetch MCP vs Manual Web Browsing

| Feature | Fetch MCP | Manual Browsing |
|---------|-----------|-----------------|
| **Interface** | Natural language | Web browser |
| **Speed** | ✅ Instant | ❌ Manual |
| **Integration** | ✅ Direct to Claude | ❌ Copy/paste |
| **Context** | ✅ Maintains context | ❌ Lost |
| **Automation** | ✅ Yes | ❌ No |
| **JavaScript** | ❌ No | ✅ Yes |

**When to use Fetch MCP:** Documentation, APIs, JSON data, automation
**When to use Manual:** JavaScript-heavy sites, authentication, complex navigation

## 🐛 Troubleshooting

### Server Not Connected

**Problem:** `fetch - ✗ Failed to connect`

**Solution:**
1. Check that npx is installed: `which npx`
2. Test manual run: `npx @modelcontextprotocol/server-fetch`
3. Restart Claude Code

### Fetch Failed

**Problem:** "Failed to fetch URL"

**Solution:**
- Verify URL is valid and accessible
- Check internet connection
- Ensure URL is publicly accessible (not behind auth)
- Try URL in browser first

### Timeout Error

**Problem:** "Request timed out"

**Solution:**
- URL may be slow to respond
- Server may be down
- Try again later
- Check if URL requires authentication

### CORS Error

**Problem:** "CORS policy blocked request"

**Solution:**
- This is a browser-specific error; MCP server shouldn't see this
- If you do, the server might be blocking API requests
- Try fetching the main page instead of API endpoint

## 📚 Best Practices

### Effective URL Fetching

✅ **DO:**
- Fetch from official documentation sites
- Use stable, versioned URLs
- Fetch from public APIs
- Cache frequently accessed content (mental note)

❌ **DON'T:**
- Fetch from localhost
- Fetch from private networks
- Fetch extremely large files
- Spam the same URL repeatedly

### Content Types

- **HTML Pages** - Documentation, articles, guides
- **JSON APIs** - Public API endpoints
- **Plain Text** - RESTful text responses, logs
- **Markdown** - README files, documentation

### Rate Limiting

- Be respectful of target servers
- Don't fetch the same URL repeatedly
- Space out requests to the same domain
- Use cached results when possible

## 📚 Common Use Cases

### 1. Framework Documentation
```
"Fetch the FastAPI security documentation"
"Get the Next.js data fetching guide"
```

### 2. API References
```
"Fetch the OpenAI API reference for function calling"
"Get the Vercel API docs for deployments"
```

### 3. Package Information
```
"Fetch the package.json from the SQLModel GitHub repo"
"Get the latest version info for @anthropic/sdk"
```

### 4. Community Resources
```
"Fetch this blog post about FastAPI best practices: [URL]"
"Get this tutorial on Next.js app router: [URL]"
```

## 📚 Resources

- [MCP Fetch Server Documentation](https://github.com/modelcontextprotocol/servers/tree/main/src/fetch)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Claude Code MCP Guide](https://docs.anthropic.com/claude/docs/mcp)

## 🔗 Related MCP Servers

Other essential MCP servers in this project:
- `filesystem` - File system operations
- `git` - Git repository operations
- `memory` - Persistent memory storage
- `github` - GitHub API operations

## ✅ Verification Checklist

- ✅ Fetch MCP server installed
- ✅ Configuration added to ~/.claude.json
- ✅ Documentation available
- ✅ Internet connection available
- ✅ Ready to use

---

**Status:** Ready to use!

**Next Step:** Try asking Claude to "Fetch https://httpbin.org/json and show the data"
