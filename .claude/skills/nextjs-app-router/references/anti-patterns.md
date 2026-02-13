# Next.js App Router Anti-Patterns Guide

Common mistakes and how to avoid them in Next.js App Router development.

## 1. Using Client Components Unnecessarily

**Problem:** Adding "use client" when not needed.

```tsx
// BAD: Unnecessary client component
"use client"

export function UserProfile({ user }) {
  return (
    <div>
      <h1>{user.name}</h1>
      <p>{user.email}</p>
    </div>
  )
}

// GOOD: Server component (default)
export function UserProfile({ user }) {
  return (
    <div>
      <h1>{user.name}</h1>
      <p>{user.email}</p>
    </div>
  )
}
```

**When to use "use client":**
- useState, useEffect, useContext
- Browser APIs (localStorage, window)
- Event handlers (onClick, onChange)
- Third-party libraries requiring browser

## 2. Fetching in Client Components

**Problem:** Fetching data client-side when server-side is possible.

```tsx
// BAD: Client-side fetch
"use client"

import { useEffect, useState } from 'react'

export function UserList() {
  const [users, setUsers] = useState([])

  useEffect(() => {
    fetch('/api/users').then(r => r.json()).then(setUsers)
  }, [])

  return <ul>{users.map(u => <li key={u.id}>{u.name}</li>)}</ul>
}

// GOOD: Server component fetch
export async function UserList() {
  const users = await fetch('http://localhost:8000/api/users').then(r => r.json())
  return <ul>{users.map(u => <li key={u.id}>{u.name}</li>)}</ul>
}
```

## 3. Not Handling Loading States

**Problem:** No loading UI during data fetching.

```tsx
// BAD: No loading state
// app/users/page.tsx
export default async function UsersPage() {
  const users = await fetch('/api/users').then(r => r.json())
  return <UserList users={users} />
}

// GOOD: Add loading.tsx
// app/users/loading.tsx
export default function Loading() {
  return <div className="animate-pulse">Loading users...</div>
}

// app/users/page.tsx
export default async function UsersPage() {
  const users = await fetch('/api/users').then(r => r.json())
  return <UserList users={users} />
}
```

## 4. Ignoring Error Boundaries

**Problem:** No error handling for failed requests.

```tsx
// BAD: Errors crash the page
export default async function UsersPage() {
  const users = await fetch('/api/users').then(r => r.json())
  return <UserList users={users} />
}

// GOOD: Add error.tsx
// app/users/error.tsx
'use client'

export default function Error({ error, reset }) {
  return (
    <div>
      <h2>Failed to load users</h2>
      <p>{error.message}</p>
      <button onClick={reset}>Retry</button>
    </div>
  )
}
```

## 5. Not Revalidating After Mutations

**Problem:** Stale data after create/update/delete.

```tsx
// BAD: Data not refreshed after mutation
'use server'

export async function createUser(formData: FormData) {
  await fetch('/api/users', {
    method: 'POST',
    body: JSON.stringify({ name: formData.get('name') })
  })
  // Page still shows old data!
}

// GOOD: Revalidate after mutation
'use server'

import { revalidatePath } from 'next/cache'

export async function createUser(formData: FormData) {
  await fetch('/api/users', {
    method: 'POST',
    body: JSON.stringify({ name: formData.get('name') })
  })
  revalidatePath('/users')  // Refresh the page data
}
```

## 6. Exposing Secrets in Client Code

**Problem:** Using secret env vars in client components.

```tsx
// BAD: Secret exposed to browser
"use client"

const API_KEY = process.env.API_SECRET_KEY  // undefined in browser!

// GOOD: Only use NEXT_PUBLIC_ in client
"use client"

const API_URL = process.env.NEXT_PUBLIC_API_URL  // Works

// GOOD: Keep secrets server-side
// Server component or API route
const API_KEY = process.env.API_SECRET_KEY  // Works
```

## 7. Prop Drilling Through Layouts

**Problem:** Passing props through multiple layout levels.

```tsx
// BAD: Prop drilling
// app/layout.tsx
export default function Layout({ children }) {
  const user = await getUser()
  return <div>{React.cloneElement(children, { user })}</div>  // Doesn't work!
}

// GOOD: Use React Context or fetch in each component
// components/UserProvider.tsx
"use client"
const UserContext = createContext(null)

export function UserProvider({ children }) {
  const [user, setUser] = useState(null)
  useEffect(() => { fetchUser().then(setUser) }, [])
  return <UserContext.Provider value={user}>{children}</UserContext.Provider>
}

// Or fetch directly in the component that needs it
export async function UserProfile() {
  const user = await getUser()  // Server component
  return <div>{user.name}</div>
}
```

## 8. Wrong Caching Strategy

**Problem:** Using wrong cache options.

```tsx
// BAD: Cached data that should be fresh
async function getNotifications() {
  const res = await fetch('/api/notifications')  // Cached by default!
  return res.json()
}

// GOOD: Disable cache for dynamic data
async function getNotifications() {
  const res = await fetch('/api/notifications', {
    cache: 'no-store'  // Always fresh
  })
  return res.json()
}

// GOOD: Revalidate periodically
async function getPosts() {
  const res = await fetch('/api/posts', {
    next: { revalidate: 60 }  // Refresh every 60 seconds
  })
  return res.json()
}
```

## 9. Mixing Server and Client Logic

**Problem:** Importing server code into client components.

```tsx
// BAD: Server code in client component
"use client"

import { db } from '@/lib/database'  // Error!

export function UserForm() {
  const handleSubmit = async () => {
    await db.users.create(...)  // Can't access DB from browser
  }
}

// GOOD: Use Server Actions
// actions.ts
'use server'

import { db } from '@/lib/database'

export async function createUser(formData: FormData) {
  await db.users.create(...)
}

// UserForm.tsx
"use client"

import { createUser } from './actions'

export function UserForm() {
  return <form action={createUser}>...</form>
}
```

## 10. Not Using TypeScript Properly

**Problem:** Missing types for props and API responses.

```tsx
// BAD: No types
export function UserCard({ user }) {
  return <div>{user.naem}</div>  // Typo not caught!
}

// GOOD: Type everything
interface User {
  id: number
  name: string
  email: string
}

export function UserCard({ user }: { user: User }) {
  return <div>{user.name}</div>  // Typo would be caught
}
```

## Quick Checklist

Before deploying, verify:

- [ ] Only "use client" where truly needed
- [ ] All pages have loading.tsx
- [ ] All pages have error.tsx
- [ ] Mutations call revalidatePath
- [ ] No NEXT_PUBLIC_ vars contain secrets
- [ ] Cache strategy appropriate for each fetch
- [ ] Server Actions for mutations
- [ ] TypeScript types for all props
