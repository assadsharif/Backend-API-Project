---
name: openai-chatkit
description: Build AI-powered chat interfaces using OpenAI ChatKit SDK. Use when implementing conversational UIs with React, setting up ChatKit backends (OpenAI-hosted or self-hosted), integrating real-time streaming, handling file uploads, or connecting to agent workflows. Triggers include "ChatKit", "chat UI", "conversational interface", "chat component", "message streaming", or requests to build chat experiences with OpenAI.
---

# OpenAI ChatKit SDK

Build production-ready AI chat interfaces with minimal setup.

## Required Clarifications

Before implementing, clarify:

1. **Backend type**: OpenAI-hosted (managed) or self-hosted (Python)?
2. **Framework**: React (recommended) or vanilla JS?
3. **Features needed**: Streaming, file upload, tool display, threading?

## Scope

**Does**: Chat UI components, session management, streaming, file uploads, tool invocation display, theming.

**Does NOT**: Agent logic (use openai-agents-sdk), authentication, database persistence, rate limiting.

## Installation

```bash
# React (recommended)
npm install @openai/chatkit-react

# Python backend (self-hosted only)
pip install openai-chatkit
```

## Backend Setup

### OpenAI-Hosted (Managed)

Requires Agent Builder workflow. OpenAI manages infrastructure.

```typescript
// Server: /api/session endpoint
import { ChatKit } from '@openai/chatkit';

const chatkit = new ChatKit({ apiKey: process.env.OPENAI_API_KEY });

app.post('/api/session', async (req, res) => {
  const session = await chatkit.sessions.create({
    workflow_id: process.env.WORKFLOW_ID  // From Agent Builder
  });
  res.json({ clientSecret: session.client_secret });
});
```

### Self-Hosted (Python)

Full infrastructure control. Implement your own agent logic.

```python
from fastapi import FastAPI
from openai_chatkit import ChatKitServer

app = FastAPI()
chatkit = ChatKitServer()

@app.post("/api/chat")
async def chat(message: str):
    response = await chatkit.process(message)
    return {"response": response}
```

## React Integration

### Minimal Setup

```tsx
import { ChatKitProvider, ChatWindow } from '@openai/chatkit-react';

function App() {
  return (
    <ChatKitProvider sessionEndpoint="/api/session">
      <ChatWindow />
    </ChatKitProvider>
  );
}
```

### useChatKit Hook

```tsx
const {
  messages,       // Message[] - conversation history
  sendMessage,    // (text: string) => Promise<void>
  isLoading,      // boolean - processing state
  error,          // Error | null
  clearMessages,  // () => void - reset conversation
  retry,          // () => void - retry failed message
} = useChatKit();
```

### Custom UI

```tsx
function CustomChat() {
  const { messages, sendMessage, isLoading } = useChatKit();
  const [input, setInput] = useState('');

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    await sendMessage(input);
    setInput('');
  };

  return (
    <div>
      {messages.map(msg => (
        <div key={msg.id} data-role={msg.role}>{msg.content}</div>
      ))}
      <form onSubmit={handleSubmit}>
        <input value={input} onChange={e => setInput(e.target.value)} />
        <button disabled={isLoading}>Send</button>
      </form>
    </div>
  );
}
```

## Customization

```tsx
<ChatWindow
  theme={{
    primaryColor: '#1877f2',
    backgroundColor: '#ffffff',
    fontFamily: 'Inter, sans-serif'
  }}
  showToolCalls={true}      // Display agent tool invocations
  showTimestamps={true}     // Show message times
  placeholder="Ask anything..."
/>
```

## Error Handling

```tsx
function ChatWithErrorBoundary() {
  const { error, retry } = useChatKit();

  if (error) {
    return (
      <div role="alert">
        <p>Error: {error.message}</p>
        <button onClick={retry}>Retry</button>
      </div>
    );
  }

  return <ChatWindow />;
}
```

## Output Checklist

Before delivery, verify:

- [ ] Session endpoint returns `clientSecret` (not full API key)
- [ ] `OPENAI_API_KEY` in server environment, never exposed to client
- [ ] Error boundary wraps ChatKit components
- [ ] Loading states shown during message processing
- [ ] Streaming enabled for long responses (`config={{ streaming: true }}`)

## Must Avoid

- Exposing API keys to frontend
- Creating sessions client-side
- Missing error boundaries (crashes propagate)
- Blocking UI during message sends (use `isLoading`)
- Hardcoding workflow IDs (use environment variables)

## Resources

| Resource | URL | Use For |
|----------|-----|---------|
| ChatKit.js Docs | https://openai.github.io/chatkit-js/ | React API reference |
| Python SDK | https://openai.github.io/chatkit-python/ | Self-hosted backend |
| Advanced Samples | https://github.com/openai/openai-chatkit-advanced-samples | Complex patterns |

For patterns not covered, fetch latest docs from URLs above.
