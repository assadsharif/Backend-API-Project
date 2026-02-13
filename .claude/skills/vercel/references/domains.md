# Vercel Custom Domains Guide

Complete guide for managing custom domains and SSL certificates on Vercel.

## Overview

Vercel provides automatic HTTPS for all deployments, including custom domains. This guide covers domain configuration, DNS setup, SSL certificate management, and troubleshooting.

## Domain Types

### Vercel Domains

**Free `.vercel.app` domains:**
- Automatically assigned: `project-name-hash.vercel.app`
- Production alias: `project-name.vercel.app`
- Preview deployments: `project-name-git-branch-team.vercel.app`
- HTTPS enabled by default
- No configuration required

### Custom Domains

**Your own domain:**
- Purchase from registrar (Namecheap, GoDaddy, Google Domains, etc.)
- Point DNS to Vercel
- Automatic SSL certificate provisioning
- Support for apex domains and subdomains

## Adding Custom Domain

### Via Dashboard

1. Go to project settings on Vercel dashboard
2. Navigate to **Domains** section
3. Click **Add Domain**
4. Enter domain name (e.g., `example.com` or `www.example.com`)
5. Click **Add**
6. Follow DNS configuration instructions

### Via CLI

```bash
# Add domain to project
vercel domains add example.com

# Add domain to specific project
vercel domains add example.com --project=my-project
```

## DNS Configuration

### Option 1: Apex Domain (example.com)

**Recommended: Use ALIAS/ANAME record**

Configure at your DNS provider:

```
Type: ALIAS (or ANAME)
Name: @
Value: cname.vercel-dns.com
```

**Alternative: Use A records**

```
Type: A
Name: @
Value: 76.76.21.21
```

**Note:** A records don't support automatic failover. ALIAS/ANAME is preferred.

### Option 2: Subdomain (www.example.com)

**Use CNAME record**

Configure at your DNS provider:

```
Type: CNAME
Name: www
Value: cname.vercel-dns.com
```

### Option 3: Both Apex and WWW

**Configure both:**

```
# Apex domain
Type: ALIAS
Name: @
Value: cname.vercel-dns.com

# WWW subdomain
Type: CNAME
Name: www
Value: cname.vercel-dns.com
```

**Set redirect in Vercel:**
- Choose which is primary (e.g., `example.com`)
- Vercel automatically redirects the other (e.g., `www.example.com` → `example.com`)

## DNS Provider Examples

### Namecheap

1. Go to **Advanced DNS** tab
2. Add record:
   - **Type**: CNAME Record
   - **Host**: www
   - **Value**: cname.vercel-dns.com
   - **TTL**: Automatic

### GoDaddy

1. Go to **DNS Management**
2. Add record:
   - **Type**: CNAME
   - **Name**: www
   - **Value**: cname.vercel-dns.com
   - **TTL**: 1 Hour

### Cloudflare

1. Go to **DNS** settings
2. Add record:
   - **Type**: CNAME
   - **Name**: www
   - **Target**: cname.vercel-dns.com
   - **Proxy status**: DNS only (gray cloud)
   - **TTL**: Auto

**Important:** Disable Cloudflare proxy (orange cloud) initially. Enable after domain verification.

### Google Domains

1. Go to **DNS** settings
2. Add record:
   - **Type**: CNAME
   - **Host**: www
   - **Data**: cname.vercel-dns.com
   - **TTL**: 1 hour

## Vercel DNS (Recommended)

### Benefits

- Automatic configuration
- No manual DNS setup
- Built-in DDoS protection
- Edge caching
- Fastest propagation

### Setup

1. Transfer nameservers to Vercel
2. Update at your registrar:
   ```
   ns1.vercel-dns.com
   ns2.vercel-dns.com
   ```
3. Domains managed entirely through Vercel dashboard

## SSL Certificates

### Automatic Provisioning

Vercel automatically provisions SSL certificates using Let's Encrypt:

1. Add domain to project
2. Configure DNS correctly
3. Wait for verification (usually < 5 minutes)
4. Certificate issued automatically
5. Auto-renewal every 60 days

### Certificate Details

- **Issuer**: Let's Encrypt
- **Type**: Domain Validation (DV)
- **Validity**: 90 days
- **Renewal**: Automatic at 60 days
- **Protocols**: TLS 1.2, TLS 1.3
- **Cipher suites**: Modern, secure defaults

### Wildcard Certificates

Vercel supports wildcard domains:

```bash
# Add wildcard domain
vercel domains add *.example.com
```

**DNS Configuration:**

```
Type: CNAME
Name: *
Value: cname.vercel-dns.com
```

**Use cases:**
- `api.example.com`
- `blog.example.com`
- `docs.example.com`

All subdomains automatically get SSL certificates.

## Domain Verification

### Verification Process

1. Add domain in Vercel
2. Vercel provides DNS instructions
3. Configure DNS at your provider
4. Vercel checks DNS records (every few minutes)
5. Once verified, SSL certificate is issued
6. Domain becomes active

### Check Verification Status

**Via Dashboard:**
- Go to project → Domains
- Look for status indicator:
  - 🟡 **Pending**: Waiting for DNS
  - 🔴 **Invalid**: DNS misconfigured
  - 🟢 **Valid**: Active and working

**Via CLI:**

```bash
vercel domains verify example.com
```

### Manual Verification Trigger

```bash
# Force verification check
vercel domains verify example.com
```

## Redirect Rules

### WWW to Non-WWW

Add both domains, Vercel automatically redirects:

```
www.example.com → example.com (301 redirect)
```

**Primary domain**: Set in Vercel dashboard under Domains

### Non-WWW to WWW

Same as above, but set `www.example.com` as primary:

```
example.com → www.example.com (301 redirect)
```

### Custom Redirects

Use `vercel.json` for custom redirects:

```json
{
  "redirects": [
    {
      "source": "/old-path",
      "destination": "/new-path",
      "permanent": true
    },
    {
      "source": "/docs/:path*",
      "destination": "https://docs.example.com/:path*",
      "permanent": false
    }
  ]
}
```

## Domain Management

### List Domains

**Via Dashboard:**
- Go to project settings → Domains

**Via CLI:**

```bash
# List all domains
vercel domains ls

# List for specific project
vercel project ls --project-name=my-project
```

### Remove Domain

**Via Dashboard:**
- Go to project → Domains
- Click domain → Remove

**Via CLI:**

```bash
vercel domains rm example.com
```

### Transfer Domain

Move domain between projects:

1. Remove from current project
2. Add to new project
3. DNS remains unchanged

## Advanced Configuration

### Multiple Domains

Point multiple domains to same project:

```bash
vercel domains add example.com
vercel domains add example.org
vercel domains add example.net
```

All domains serve the same content. Use redirect rules if needed.

### Environment-Specific Domains

Different domains for production/preview:

- **Production**: `example.com`
- **Preview**: `staging.example.com`

Configure in `vercel.json`:

```json
{
  "github": {
    "silent": true,
    "autoAlias": true
  },
  "alias": ["example.com"],
  "scope": "my-team"
}
```

### Git Branch Domains

Automatic domains for Git branches:

- `main` branch → `example.com`
- `develop` branch → `develop.example.com`
- `feature-x` branch → `feature-x.example.com`

Configure wildcard domain `*.example.com` in Vercel.

## Troubleshooting

### Domain Not Verifying

**Check:**
1. DNS records configured correctly
2. TTL expired (wait for propagation)
3. No conflicting records (A/CNAME)
4. Nameservers responding (use `dig` or `nslookup`)

**Verify DNS propagation:**

```bash
# Check DNS records
dig example.com
dig www.example.com

# Check from specific nameserver
dig @8.8.8.8 example.com

# Check CNAME
dig www.example.com CNAME
```

### SSL Certificate Not Issuing

**Check:**
1. Domain verified successfully
2. DNS pointing to Vercel
3. No firewall blocking Let's Encrypt validation
4. CAA records allow Let's Encrypt (if set)

**CAA Record (if present):**

```
Type: CAA
Name: @
Value: 0 issue "letsencrypt.org"
```

### Redirect Loop

**Causes:**
- Cloudflare proxy enabled with incorrect SSL mode
- Multiple domains without clear primary

**Fix:**
1. Set Cloudflare SSL to "Full" or "Full (Strict)"
2. Ensure one domain is marked as primary in Vercel
3. Clear browser cache

### DNS Propagation Delays

**Timeline:**
- Cloudflare: ~2 minutes
- Namecheap: 5-30 minutes
- GoDaddy: 1 hour
- Others: up to 48 hours

**Speed up:**
- Lower TTL before changes (e.g., 300 seconds)
- Use Vercel DNS for instant propagation
- Clear DNS cache: `sudo dscacheutil -flushcache` (macOS)

### HTTPS Not Working

**Check:**
1. Domain verified and active
2. Certificate issued (check in dashboard)
3. No mixed content errors (HTTP resources on HTTPS page)
4. Browser cache cleared

**Force HTTPS:**

Add to `vercel.json`:

```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "Strict-Transport-Security",
          "value": "max-age=31536000; includeSubDomains"
        }
      ]
    }
  ]
}
```

## Best Practices

1. **Use Vercel DNS**: Simplest setup, fastest propagation
2. **Set low TTL initially**: Easier to fix DNS mistakes
3. **Verify before going live**: Test with preview domains first
4. **Enable HSTS**: Force HTTPS for security
5. **Monitor certificate expiry**: Though auto-renewed, monitor for issues
6. **Use apex domain**: Better for SEO, redirect www to apex
7. **Implement CSP**: Content Security Policy headers for security

## Domain Security

### DNSSEC

Enable at your DNS provider for additional security:
- Prevents DNS spoofing
- Validates DNS responses
- Supported by most registrars

### HSTS Preload

Submit domain to HSTS preload list:
1. Add HSTS header with preload directive
2. Submit at https://hstspreload.org/
3. Browsers will only connect via HTTPS

**Header:**

```
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
```

### CAA Records

Restrict which CAs can issue certificates:

```
Type: CAA
Name: @
Value: 0 issue "letsencrypt.org"
```

## CLI Reference

```bash
# Add domain
vercel domains add example.com

# List domains
vercel domains ls

# Verify domain
vercel domains verify example.com

# Remove domain
vercel domains rm example.com

# Check domain status
vercel inspect example.com
```

## Resources

- [Vercel Domains Documentation](https://vercel.com/docs/concepts/projects/custom-domains)
- [DNS Configuration Guide](https://vercel.com/docs/concepts/projects/custom-domains#dns-configuration)
- [Let's Encrypt](https://letsencrypt.org/)
- [HSTS Preload](https://hstspreload.org/)
- [DNS Propagation Checker](https://www.whatsmydns.net/)
