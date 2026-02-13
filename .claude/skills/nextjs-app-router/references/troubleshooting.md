# Next.js App Router Troubleshooting Guide

Common issues and solutions in Next.js development.

## Build Errors

### Symptoms
- `Module not found`
- `Cannot find module`

### Solutions

```bash
# Clear cache and rebuild
rm -rf .next
rm -rf node_modules
npm install
npm run build

# Check import paths
# Use @ alias (configured in tsconfig.json)
import { api } from '@/lib/api'

# Not relative paths that might break
import { api } from '../../../lib/api'
```

## Hydration Mismatch

### Symptoms
- `Hydration failed because...`
- `Text content does not match`

### Solutions

```tsx
// Problem: Server and client render differently
// BAD: Date changes between server and client
export default function Page() {
  return <p>{new Date().toLocaleString()}</p>
}

// GOOD: Use useEffect for client-only values
'use client'
import { useState, useEffect } from 'react'

export default function Page() {
  const [date, setDate] = useState<string>('')

  useEffect(() => {
    setDate(new Date().toLocaleString())
  }, [])

  return <p>{date}</p>
}

// Or suppress hydration warning for dynamic content
<time suppressHydrationWarning>
  {new Date().toLocaleString()}
</time>
```

## Server Component in Client Component

### Symptoms
- `You're importing a component that needs useState`
- `async/await is not yet supported in Client Components`

### Solutions

```tsx
// Can't use async in client components
// BAD
'use client'
export default async function Page() {  // Error!
  const data = await fetch(...)
}

// GOOD: Keep data fetching in server components
// page.tsx (server component)
export default async function Page() {
  const data = await fetch(...)
  return <ClientComponent data={data} />
}

// ClientComponent.tsx
'use client'
export function ClientComponent({ data }) {
  const [state, setState] = useState(data)
  return ...
}
```

## API Route Not Working

### Symptoms
- 404 on API routes
- Wrong response format

### Solutions

```tsx
// Check file location and naming
// app/api/users/route.ts (correct)
// app/api/users/route.tsx (wrong extension)
// app/api/users.ts (wrong - needs route.ts)

// Export correct methods
// app/api/users/route.ts
import { NextResponse } from 'next/server'

export async function GET() {
  return NextResponse.json({ users: [] })
}

export async function POST(request: Request) {
  const body = await request.json()
  return NextResponse.json(body, { status: 201 })
}
```

## Environment Variables Not Loading

### Symptoms
- `undefined` for env vars
- Works locally but not in production

### Solutions

```bash
# Client-side: Must prefix with NEXT_PUBLIC_
NEXT_PUBLIC_API_URL=http://localhost:8000  # Accessible in browser
API_SECRET=secret  # Server-only

# Restart dev server after changing .env
npm run dev

# Check file name
.env.local      # Local dev (gitignored)
.env            # All environments
.env.production # Production only

# Verify in code
console.log(process.env.NEXT_PUBLIC_API_URL)
```

## Server Actions Not Working

### Symptoms
- Form doesn't submit
- `TypeError: action is not a function`

### Solutions

```tsx
// Ensure 'use server' directive
// app/actions.ts
'use server'  // Must be at top of file

export async function createUser(formData: FormData) {
  // ...
}

// Import and use in form
import { createUser } from './actions'

export function Form() {
  return (
    <form action={createUser}>
      <input name="email" />
      <button type="submit">Submit</button>
    </form>
  )
}
```

## Fetch Errors

### Symptoms
- `Failed to fetch`
- Data not updating

### Solutions

```tsx
// Check cache settings
// For dynamic data
const res = await fetch(url, { cache: 'no-store' })

// For revalidation
const res = await fetch(url, { next: { revalidate: 60 } })

// Handle errors
const res = await fetch(url)
if (!res.ok) {
  throw new Error(`Failed to fetch: ${res.status}`)
}

// Use absolute URLs in server components
// BAD: Relative URL
await fetch('/api/users')

// GOOD: Absolute URL
await fetch('http://localhost:8000/api/users')
```

## Styling Issues

### Symptoms
- Styles not applying
- Flash of unstyled content

### Solutions

```tsx
// Ensure Tailwind is configured
// tailwind.config.js
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
  ],
}

// Import global CSS in root layout
// app/layout.tsx
import './globals.css'

// For CSS modules
import styles from './page.module.css'
<div className={styles.container}>
```

## TypeScript Errors

### Symptoms
- Type errors in components
- `Property does not exist`

### Solutions

```tsx
// Define types for props
interface Props {
  user: {
    id: number
    name: string
  }
}

export function UserCard({ user }: Props) {
  return <div>{user.name}</div>
}

// Type API responses
interface User {
  id: number
  name: string
}

const users: User[] = await fetch(...).then(r => r.json())

// Type form data
export async function createUser(formData: FormData) {
  const email = formData.get('email') as string
}
```

## Quick Debugging

```bash
# Check build output
npm run build

# Verbose logging
DEBUG=* npm run dev

# Check for type errors
npm run lint
npx tsc --noEmit

# Clear all caches
rm -rf .next node_modules/.cache

# Check bundle size
npm run build
npx @next/bundle-analyzer
```
