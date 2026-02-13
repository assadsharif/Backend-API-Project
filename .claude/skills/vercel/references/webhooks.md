# Vercel Webhooks Guide

Complete guide for configuring and managing Vercel webhooks.

## Overview

Vercel webhooks allow you to receive real-time notifications about deployment events, enabling integration with CI/CD pipelines, monitoring systems, and custom workflows.

## Webhook Events

### Deployment Events

**deployment.created**
- Triggered when a new deployment starts
- Useful for: Starting external tests, notifying team

**deployment.ready**
- Triggered when deployment succeeds and is accessible
- Useful for: Running smoke tests, updating monitoring, sending notifications

**deployment.error**
- Triggered when deployment fails
- Useful for: Alerting team, logging failures, triggering rollback

**deployment.canceled**
- Triggered when deployment is manually canceled
- Useful for: Cleaning up resources, logging cancellations

**deployment.check-rerequested**
- Triggered when deployment checks are re-run
- Useful for: Re-running integration tests

### Project Events

**project.created**
- Triggered when new project is created
- Useful for: Setting up monitoring, configuring integrations

**project.removed**
- Triggered when project is deleted
- Useful for: Cleaning up external resources

## Configuration

### Via Dashboard

1. Go to project settings on Vercel dashboard
2. Navigate to **Webhooks** section
3. Click **Create Webhook**
4. Configure:
   - **URL**: Your webhook endpoint (must be HTTPS)
   - **Events**: Select events to subscribe to
   - **Secret**: Auto-generated for signature verification

### Via API

```bash
# Create webhook using API
curl -X POST "https://api.vercel.com/v1/integrations/webhooks" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-server.com/webhook",
    "events": ["deployment.created", "deployment.ready"],
    "projectIds": ["prj_xxx"]
  }'
```

## Webhook Payload

### Example: deployment.ready

```json
{
  "id": "evt_xxx",
  "type": "deployment.ready",
  "createdAt": 1234567890,
  "payload": {
    "deployment": {
      "id": "dpl_xxx",
      "url": "my-app-abc123.vercel.app",
      "name": "my-app",
      "inspectorUrl": "https://vercel.com/my-team/my-app/abc123",
      "projectId": "prj_xxx",
      "target": "production",
      "aliasAssigned": true,
      "aliasError": null,
      "createdAt": 1234567890,
      "readyAt": 1234567900,
      "buildingAt": 1234567895,
      "creator": {
        "uid": "usr_xxx",
        "email": "user@example.com",
        "username": "user"
      },
      "meta": {
        "githubCommitRef": "main",
        "githubCommitSha": "abc123",
        "githubCommitMessage": "Update feature",
        "githubCommitAuthorName": "User Name"
      }
    },
    "project": {
      "id": "prj_xxx",
      "name": "my-app"
    },
    "team": {
      "id": "team_xxx",
      "name": "My Team"
    }
  }
}
```

## Security

### Signature Verification

Vercel signs webhook requests with HMAC-SHA256. Verify signatures to ensure authenticity.

**Header**: `x-vercel-signature`

**Verification Example (Node.js)**:

```javascript
const crypto = require('crypto');

function verifyWebhook(payload, signature, secret) {
  const hmac = crypto.createHmac('sha256', secret);
  const digest = hmac.update(payload).digest('hex');
  return signature === digest;
}

// Express middleware
app.post('/webhook', (req, res) => {
  const signature = req.headers['x-vercel-signature'];
  const payload = JSON.stringify(req.body);

  if (!verifyWebhook(payload, signature, process.env.WEBHOOK_SECRET)) {
    return res.status(401).send('Invalid signature');
  }

  // Process webhook
  res.status(200).send('OK');
});
```

**Verification Example (Python)**:

```python
import hmac
import hashlib

def verify_webhook(payload: str, signature: str, secret: str) -> bool:
    digest = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return signature == digest

# FastAPI endpoint
@app.post("/webhook")
async def webhook(request: Request):
    signature = request.headers.get("x-vercel-signature")
    payload = await request.body()

    if not verify_webhook(payload.decode(), signature, WEBHOOK_SECRET):
        raise HTTPException(401, "Invalid signature")

    # Process webhook
    return {"status": "ok"}
```

### Best Practices

1. **Always verify signatures** - Never trust webhook payloads without verification
2. **Use HTTPS endpoints** - Vercel requires HTTPS for webhook URLs
3. **Rotate secrets** - Periodically regenerate webhook secrets
4. **Implement idempotency** - Handle duplicate webhook deliveries gracefully
5. **Return quickly** - Respond with 200 status immediately, process asynchronously

## Testing Webhooks

### Local Testing with ngrok

```bash
# Start ngrok tunnel
ngrok http 3000

# Use ngrok URL in Vercel webhook configuration
# Example: https://abc123.ngrok.io/webhook
```

### Manual Trigger

Manually trigger deployments to test webhooks:

```bash
# Trigger production deployment
vercel --prod --yes

# Trigger preview deployment
vercel --yes
```

### Webhook Logs

View webhook delivery logs in Vercel dashboard:
1. Go to project settings
2. Navigate to **Webhooks**
3. Click on webhook
4. View **Recent Deliveries**

Shows:
- Request/response headers
- Payload
- Response status
- Timestamp
- Retry attempts

## Common Use Cases

### CI/CD Integration

Trigger external tests when deployment is ready:

```javascript
app.post('/webhook', async (req, res) => {
  const { type, payload } = req.body;

  if (type === 'deployment.ready') {
    const { url, target } = payload.deployment;

    if (target === 'production') {
      // Trigger smoke tests
      await runSmokeTests(url);

      // Update monitoring
      await updateMonitoring(url);

      // Notify team
      await notifyTeam(`Production deployed: ${url}`);
    }
  }

  res.status(200).send('OK');
});
```

### Slack Notifications

Send deployment notifications to Slack:

```javascript
app.post('/webhook', async (req, res) => {
  const { type, payload } = req.body;

  if (type === 'deployment.ready') {
    const { url, creator, meta } = payload.deployment;

    await fetch(process.env.SLACK_WEBHOOK_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: `🚀 Deployment ready!`,
        blocks: [
          {
            type: 'section',
            text: {
              type: 'mrkdwn',
              text: `*URL:* ${url}\n*By:* ${creator.username}\n*Commit:* ${meta.githubCommitMessage}`
            }
          }
        ]
      })
    });
  }

  res.status(200).send('OK');
});
```

### Automatic Rollback

Monitor deployment health and rollback on failure:

```javascript
app.post('/webhook', async (req, res) => {
  const { type, payload } = req.body;

  if (type === 'deployment.ready') {
    const { url, id } = payload.deployment;

    // Wait for deployment to warm up
    await sleep(30000);

    // Run health checks
    const healthy = await checkHealth(url);

    if (!healthy) {
      // Rollback to previous deployment
      await rollback(payload.project.id);

      // Alert team
      await alertTeam(`Deployment ${id} failed health checks. Rolled back.`);
    }
  }

  res.status(200).send('OK');
});
```

## Error Handling

### Retry Logic

Vercel retries failed webhooks with exponential backoff:
- 1st retry: 1 second
- 2nd retry: 2 seconds
- 3rd retry: 4 seconds
- 4th retry: 8 seconds
- 5th retry: 16 seconds

**Total retries**: 5 attempts over ~30 seconds

### Handling Failures

Implement robust error handling:

```javascript
app.post('/webhook', async (req, res) => {
  try {
    // Process webhook
    await processWebhook(req.body);

    // Respond immediately
    res.status(200).send('OK');
  } catch (error) {
    // Log error
    console.error('Webhook processing failed:', error);

    // Return 5xx for Vercel to retry
    res.status(500).send('Processing failed');
  }
});
```

### Idempotency

Handle duplicate webhook deliveries:

```javascript
const processedEvents = new Set();

app.post('/webhook', async (req, res) => {
  const { id, type, payload } = req.body;

  // Check if already processed
  if (processedEvents.has(id)) {
    return res.status(200).send('Already processed');
  }

  // Process webhook
  await processWebhook(type, payload);

  // Mark as processed
  processedEvents.add(id);

  res.status(200).send('OK');
});
```

## Troubleshooting

### Webhook Not Firing

**Check:**
1. Webhook is enabled in dashboard
2. Correct events are selected
3. Project ID matches (if project-specific)
4. Vercel can reach your endpoint (not firewalled)

### Invalid Signature

**Check:**
1. Using correct webhook secret
2. Verifying entire raw request body
3. Not modifying payload before verification
4. Secret matches webhook configuration

### Missing Events

**Check:**
1. Event type is subscribed in webhook config
2. Deployment target matches (production vs preview)
3. Webhook delivery logs for errors
4. Your endpoint returned 200 status

### Rate Limiting

**Symptom**: Webhook deliveries failing with 429 status

**Solution**:
- Implement queuing for webhook processing
- Return 200 immediately, process asynchronously
- Scale webhook processing infrastructure

## Management

### List Webhooks

```bash
# Via Vercel CLI (not directly supported)
# Use API instead

curl "https://api.vercel.com/v1/integrations/webhooks" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Update Webhook

```bash
curl -X PATCH "https://api.vercel.com/v1/integrations/webhooks/WEBHOOK_ID" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://new-endpoint.com/webhook",
    "events": ["deployment.ready"]
  }'
```

### Delete Webhook

```bash
curl -X DELETE "https://api.vercel.com/v1/integrations/webhooks/WEBHOOK_ID" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Regenerate Secret

Via dashboard:
1. Go to project settings → Webhooks
2. Click webhook to edit
3. Click **Regenerate Secret**
4. Update your webhook handler with new secret

## Resources

- [Vercel Webhooks Documentation](https://vercel.com/docs/observability/webhooks)
- [Webhook Events Reference](https://vercel.com/docs/observability/webhooks/webhooks-api)
- [ngrok - Local Testing](https://ngrok.com/)
