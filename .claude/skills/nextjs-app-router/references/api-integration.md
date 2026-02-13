# FastAPI Backend Integration

## API Client Setup

### Basic API Client

```tsx
// lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export class APIError extends Error {
  constructor(public status: number, message: string) {
    super(message)
    this.name = 'APIError'
  }
}

async function handleResponse(res: Response) {
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Unknown error' }))
    throw new APIError(res.status, error.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

export const api = {
  todos: {
    list: async (status?: 'active' | 'completed') => {
      const url = status
        ? `${API_BASE}/api/todos?status=${status}`
        : `${API_BASE}/api/todos`
      const res = await fetch(url, { cache: 'no-store' })
      return handleResponse(res)
    },

    get: async (id: number) => {
      const res = await fetch(`${API_BASE}/api/todos/${id}`, {
        cache: 'no-store'
      })
      return handleResponse(res)
    },

    create: async (data: { title: string; status: string }) => {
      const res = await fetch(`${API_BASE}/api/todos`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      return handleResponse(res)
    },

    update: async (id: number, data: Partial<{ title: string; status: string }>) => {
      const res = await fetch(`${API_BASE}/api/todos/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      return handleResponse(res)
    },

    delete: async (id: number) => {
      const res = await fetch(`${API_BASE}/api/todos/${id}`, {
        method: 'DELETE'
      })
      if (!res.ok) {
        throw new APIError(res.status, 'Failed to delete todo')
      }
    }
  }
}
```

## Error Handling Patterns

### Global Error Boundary

```tsx
// app/error.tsx
'use client'

export default function Error({ error, reset }: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div>
      <h2>Something went wrong!</h2>
      <p>{error.message}</p>
      <button onClick={reset}>Try again</button>
    </div>
  )
}
```

### Feature-Specific Error Boundary

```tsx
// app/todos/error.tsx
'use client'

import { APIError } from '@/lib/api'

export default function TodosError({ error, reset }: {
  error: Error
  reset: () => void
}) {
  if (error instanceof APIError) {
    if (error.status === 404) {
      return <div>Todo not found</div>
    }
    if (error.status === 422) {
      return <div>Invalid todo data: {error.message}</div>
    }
    if (error.status === 500) {
      return <div>Server error. Please try again later.</div>
    }
  }

  return (
    <div>
      <h2>Failed to load todos</h2>
      <p>{error.message}</p>
      <button onClick={reset}>Retry</button>
    </div>
  )
}
```

### Try-Catch in Server Components

```tsx
// app/todos/page.tsx
import { api } from '@/lib/api'
import { notFound } from 'next/navigation'

async function TodosPage() {
  try {
    const todos = await api.todos.list()
    return <TodoList todos={todos} />
  } catch (error) {
    if (error instanceof APIError && error.status === 404) {
      notFound()
    }
    throw error // Let error boundary handle it
  }
}
```

## Loading States

### Page-Level Loading

```tsx
// app/todos/loading.tsx
export default function Loading() {
  return (
    <div>
      <h1>Todos</h1>
      <div>Loading todos...</div>
    </div>
  )
}
```

### Skeleton UI

```tsx
// app/todos/loading.tsx
export default function Loading() {
  return (
    <div>
      <h1>Todos</h1>
      <div className="space-y-2">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="h-12 bg-gray-200 animate-pulse rounded" />
        ))}
      </div>
    </div>
  )
}
```

### Streaming with Suspense

```tsx
// app/todos/page.tsx
import { Suspense } from 'react'
import { api } from '@/lib/api'

async function TodoList() {
  const todos = await api.todos.list()
  return (
    <ul>
      {todos.map(todo => (
        <li key={todo.id}>{todo.title}</li>
      ))}
    </ul>
  )
}

export default function TodosPage() {
  return (
    <div>
      <h1>Todos</h1>
      <Suspense fallback={<div>Loading todos...</div>}>
        <TodoList />
      </Suspense>
    </div>
  )
}
```

## Data Fetching Strategies

### No Caching (Dynamic Data)

```tsx
const res = await fetch('http://localhost:8000/api/todos', {
  cache: 'no-store'
})
```

### Revalidate Every N Seconds

```tsx
const res = await fetch('http://localhost:8000/api/todos', {
  next: { revalidate: 60 } // Revalidate every 60 seconds
})
```

### Revalidate on Demand

```tsx
// In server action
import { revalidatePath, revalidateTag } from 'next/cache'

export async function createTodo(formData: FormData) {
  // Create todo...
  revalidatePath('/todos') // Revalidate specific path
  // OR
  revalidateTag('todos') // Revalidate tagged requests
}
```

### Tagged Fetching

```tsx
const res = await fetch('http://localhost:8000/api/todos', {
  next: { tags: ['todos'] }
})
```

## Environment Configuration

### Environment Variables

```bash
# .env.local (development)
NEXT_PUBLIC_API_URL=http://localhost:8000
API_URL=http://localhost:8000

# .env.production (production)
NEXT_PUBLIC_API_URL=https://api.example.com
API_URL=https://api.example.com
```

### Usage in Code

```tsx
// Client-side (browser) - must start with NEXT_PUBLIC_
const apiUrl = process.env.NEXT_PUBLIC_API_URL

// Server-side (Node.js) - can use any name
const apiUrl = process.env.API_URL
```

### Type-Safe Environment Variables

```tsx
// env.ts
export const env = {
  apiUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  isDev: process.env.NODE_ENV === 'development'
}

// Usage
import { env } from '@/env'
const todos = await fetch(`${env.apiUrl}/api/todos`)
```

## CORS Handling

### FastAPI CORS Configuration

```python
# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Next.js API Route as Proxy

```tsx
// app/api/todos/route.ts
import { NextResponse } from 'next/server'

const API_BASE = process.env.API_URL || 'http://localhost:8000'

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const status = searchParams.get('status')

  const url = status
    ? `${API_BASE}/api/todos?status=${status}`
    : `${API_BASE}/api/todos`

  const res = await fetch(url)
  const data = await res.json()

  return NextResponse.json(data)
}

export async function POST(request: Request) {
  const body = await request.json()

  const res = await fetch(`${API_BASE}/api/todos`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  })

  const data = await res.json()
  return NextResponse.json(data, { status: res.status })
}
```

## TypeScript Integration

### Shared Types

```tsx
// types/todo.ts
export interface Todo {
  id: number
  title: string
  status: 'active' | 'completed'
  created_at: string
  updated_at: string
}

export type TodoCreate = Pick<Todo, 'title' | 'status'>
export type TodoUpdate = Partial<TodoCreate>
```

### API Client with Types

```tsx
// lib/api.ts
import type { Todo, TodoCreate, TodoUpdate } from '@/types/todo'

export const api = {
  todos: {
    list: async (status?: Todo['status']): Promise<Todo[]> => {
      const url = status
        ? `${API_BASE}/api/todos?status=${status}`
        : `${API_BASE}/api/todos`
      const res = await fetch(url, { cache: 'no-store' })
      return handleResponse(res)
    },

    create: async (data: TodoCreate): Promise<Todo> => {
      const res = await fetch(`${API_BASE}/api/todos`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      return handleResponse(res)
    },

    update: async (id: number, data: TodoUpdate): Promise<Todo> => {
      const res = await fetch(`${API_BASE}/api/todos/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      return handleResponse(res)
    }
  }
}
```
