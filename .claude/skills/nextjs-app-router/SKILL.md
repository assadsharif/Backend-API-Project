---
name: nextjs-app-router
description: Expert guidance for Next.js with App Router (v13+) development. Use when building Next.js applications with App Router, implementing server/client components, setting up routing, data fetching, server actions, or integrating with backend APIs. Triggers include "Next.js", "App Router", "server components", "client components", "app directory", "layout.tsx", "page.tsx", "server actions", or requests to build web frontends with Next.js.
version: "1.0"
last_verified: "2025-01"
---

# Next.js App Router

Expert guidance for Next.js with App Router (v13+) development, providing best practices and patterns for modern React applications.

## What This Skill Does

- App directory structure with layouts, pages, and route groups
- Server vs Client component decisions
- Data fetching with server-side rendering
- Server Actions for form handling and mutations
- API route integration with backend
- Error and loading state handling
- Environment configuration

## What This Skill Does NOT Do

- Backend API development (use fastapi-backend skill)
- Database operations (use sqlmodel-orm skill)
- Authentication implementation (use dedicated auth libraries)
- CSS/styling frameworks beyond basics
- Deployment or hosting configuration
- Static site generation (SSG) optimization
- Internationalization (i18n)

## Quick Start

### Initialize Next.js App

```bash
npx create-next-app@latest my-app --typescript --tailwind --app
cd my-app
npm run dev
```

### Basic App Directory Structure

```
app/
├── layout.tsx          # Root layout (required)
├── page.tsx            # Home page
├── loading.tsx         # Loading UI
├── error.tsx           # Error boundary
├── not-found.tsx       # 404 page
├── api/                # API routes
│   └── route.ts
└── [feature]/          # Feature routes
    ├── layout.tsx
    ├── page.tsx
    └── [id]/
        └── page.tsx
```

## Core Patterns

### 1. Server vs Client Components

**Server Components (default)** - No directive needed:
```tsx
// app/todos/page.tsx
async function TodosPage() {
  const todos = await fetch('http://localhost:8000/api/todos').then(r => r.json())
  return <TodoList todos={todos} />
}
```

**Client Components** - Add `"use client"`:
```tsx
// components/TodoList.tsx
"use client"

import { useState } from 'react'

export function TodoList({ todos }) {
  const [filter, setFilter] = useState('all')
  return (
    <select onChange={(e) => setFilter(e.target.value)}>
      <option value="all">All</option>
      <option value="active">Active</option>
    </select>
  )
}
```

### 2. Data Fetching

```tsx
// app/todos/page.tsx
async function TodosPage() {
  const res = await fetch('http://localhost:8000/api/todos', {
    cache: 'no-store' // Disable caching for dynamic data
  })
  const todos = await res.json()
  return <TodoList todos={todos} />
}
```

### 3. Server Actions

```tsx
// app/todos/actions.ts
'use server'

import { revalidatePath } from 'next/cache'
import { redirect } from 'next/navigation'

export async function createTodo(formData: FormData) {
  const title = formData.get('title')

  const res = await fetch('http://localhost:8000/api/todos', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, status: 'active' })
  })

  if (!res.ok) throw new Error('Failed to create todo')

  revalidatePath('/todos')
  redirect('/todos')
}
```

```tsx
// app/todos/CreateTodoForm.tsx
import { createTodo } from './actions'

export function CreateTodoForm() {
  return (
    <form action={createTodo}>
      <input type="text" name="title" required />
      <button type="submit">Create</button>
    </form>
  )
}
```

### 4. API Client Pattern

```tsx
// lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const api = {
  todos: {
    list: async () => {
      const res = await fetch(`${API_BASE}/api/todos`)
      if (!res.ok) throw new Error('Failed to fetch todos')
      return res.json()
    },
    create: async (data: { title: string; status: string }) => {
      const res = await fetch(`${API_BASE}/api/todos`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      if (!res.ok) throw new Error('Failed to create todo')
      return res.json()
    },
    update: async (id: number, data: Partial<{ title: string; status: string }>) => {
      const res = await fetch(`${API_BASE}/api/todos/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      if (!res.ok) throw new Error('Failed to update todo')
      return res.json()
    },
    delete: async (id: number) => {
      const res = await fetch(`${API_BASE}/api/todos/${id}`, { method: 'DELETE' })
      if (!res.ok) throw new Error('Failed to delete todo')
    }
  }
}
```

### 5. Error and Loading States

```tsx
// app/todos/loading.tsx
export default function Loading() {
  return <div>Loading todos...</div>
}

// app/todos/error.tsx
'use client'

export default function Error({ error, reset }) {
  return (
    <div>
      <h2>Failed to load todos</h2>
      <button onClick={reset}>Try again</button>
    </div>
  )
}
```

## Output Specification

A properly configured Next.js frontend includes:

- [ ] `app/layout.tsx` with root HTML structure
- [ ] `app/page.tsx` as entry point
- [ ] `app/loading.tsx` for loading states
- [ ] `app/error.tsx` for error boundaries
- [ ] `lib/api.ts` with API client functions
- [ ] `.env.local` with NEXT_PUBLIC_API_URL
- [ ] Server components for data fetching
- [ ] Client components only where interactivity needed

## Quality Gate Checklist

Before marking frontend complete, verify:

- [ ] All pages have loading.tsx states
- [ ] Error boundaries handle API failures gracefully
- [ ] Forms use Server Actions or proper handlers
- [ ] API_URL loaded from environment variables
- [ ] No NEXT_PUBLIC_ vars contain secrets
- [ ] TypeScript types defined for API responses
- [ ] Client components minimized (only for interactivity)
- [ ] revalidatePath called after mutations

## Environment Configuration

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
API_URL=http://localhost:8000
```

- `NEXT_PUBLIC_*` - Accessible in client components
- No prefix - Server-only (secrets safe here)

## Official Documentation

| Resource | URL | Use For |
|----------|-----|---------|
| Next.js Docs | https://nextjs.org/docs | Core concepts, App Router |
| App Router | https://nextjs.org/docs/app | Routing, layouts, server components |
| Server Actions | https://nextjs.org/docs/app/api-reference/functions/server-actions | Form handling, mutations |
| Data Fetching | https://nextjs.org/docs/app/building-your-application/data-fetching | fetch, caching, revalidation |
| React Docs | https://react.dev/ | Hooks, components, patterns |

For patterns not covered here, consult official docs above.

## Keeping Current

- **Last verified:** 2025-01
- **Check for updates:** https://nextjs.org/blog
- Next.js releases frequently; verify patterns against current version
- App Router patterns differ significantly from Pages Router

## TypeScript Types

```tsx
// types/todo.ts
export interface Todo {
  id: number
  title: string
  status: 'active' | 'completed'
  created_at: string
  updated_at: string
}
```

## Reference Guides

| File | When to Read |
|------|--------------|
| `references/form-patterns.md` | useFormState, optimistic updates |
| `references/api-integration.md` | FastAPI integration, error handling |
| `references/anti-patterns.md` | Common mistakes and how to avoid them |
| `references/troubleshooting.md` | Common Next.js issues and solutions |
| `../INTEGRATION.md` | How all 5 skills work together |

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/init_nextjs.sh` | Initialize Next.js project with best practices |
