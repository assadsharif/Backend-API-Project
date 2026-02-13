# Form Handling Patterns

## Client-Side Form with useState

```tsx
"use client"

import { useState } from 'react'
import { api } from '@/lib/api'

export function CreateTodoForm() {
  const [title, setTitle] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      await api.todos.create({ title, status: 'active' })
      setTitle('') // Reset form
      window.location.reload() // Refresh data
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Todo title"
        required
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Creating...' : 'Create'}
      </button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </form>
  )
}
```

## Server Action Form (Recommended)

```tsx
// app/todos/actions.ts
'use server'

import { revalidatePath } from 'next/cache'
import { redirect } from 'next/navigation'

export async function createTodo(formData: FormData) {
  const title = formData.get('title') as string

  if (!title || title.trim().length === 0) {
    throw new Error('Title is required')
  }

  const res = await fetch('http://localhost:8000/api/todos', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, status: 'active' })
  })

  if (!res.ok) {
    const error = await res.json()
    throw new Error(error.detail || 'Failed to create todo')
  }

  revalidatePath('/todos')
  redirect('/todos')
}

export async function updateTodo(id: number, formData: FormData) {
  const title = formData.get('title') as string
  const status = formData.get('status') as string

  const res = await fetch(`http://localhost:8000/api/todos/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, status })
  })

  if (!res.ok) {
    const error = await res.json()
    throw new Error(error.detail || 'Failed to update todo')
  }

  revalidatePath('/todos')
  redirect('/todos')
}

export async function deleteTodo(id: number) {
  const res = await fetch(`http://localhost:8000/api/todos/${id}`, {
    method: 'DELETE'
  })

  if (!res.ok) {
    throw new Error('Failed to delete todo')
  }

  revalidatePath('/todos')
}
```

```tsx
// app/todos/CreateTodoForm.tsx
import { createTodo } from './actions'

export function CreateTodoForm() {
  return (
    <form action={createTodo}>
      <input type="text" name="title" placeholder="Todo title" required />
      <button type="submit">Create</button>
    </form>
  )
}
```

## Form with useFormStatus (Pending State)

```tsx
"use client"

import { useFormStatus } from 'react-dom'
import { createTodo } from './actions'

function SubmitButton() {
  const { pending } = useFormStatus()

  return (
    <button type="submit" disabled={pending}>
      {pending ? 'Creating...' : 'Create Todo'}
    </button>
  )
}

export function CreateTodoForm() {
  return (
    <form action={createTodo}>
      <input type="text" name="title" placeholder="Todo title" required />
      <SubmitButton />
    </form>
  )
}
```

## Form with Validation and Error Display

```tsx
"use client"

import { useFormState } from 'react-dom'
import { createTodo } from './actions'

// Update server action to return state
export async function createTodo(prevState: any, formData: FormData) {
  const title = formData.get('title') as string

  if (!title || title.trim().length === 0) {
    return { error: 'Title is required' }
  }

  try {
    const res = await fetch('http://localhost:8000/api/todos', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, status: 'active' })
    })

    if (!res.ok) {
      const error = await res.json()
      return { error: error.detail || 'Failed to create todo' }
    }

    revalidatePath('/todos')
    return { success: true }
  } catch (err) {
    return { error: 'Network error' }
  }
}

// Form component
export function CreateTodoForm() {
  const [state, formAction] = useFormState(createTodo, null)

  return (
    <form action={formAction}>
      <input type="text" name="title" placeholder="Todo title" required />
      <button type="submit">Create</button>
      {state?.error && <p style={{ color: 'red' }}>{state.error}</p>}
      {state?.success && <p style={{ color: 'green' }}>Todo created!</p>}
    </form>
  )
}
```

## Delete with Confirmation

```tsx
"use client"

import { deleteTodo } from './actions'
import { useTransition } from 'react'

export function DeleteButton({ id }: { id: number }) {
  const [isPending, startTransition] = useTransition()

  function handleDelete() {
    if (confirm('Are you sure you want to delete this todo?')) {
      startTransition(async () => {
        await deleteTodo(id)
      })
    }
  }

  return (
    <button onClick={handleDelete} disabled={isPending}>
      {isPending ? 'Deleting...' : 'Delete'}
    </button>
  )
}
```

## Optimistic Updates

```tsx
"use client"

import { useOptimistic } from 'react'
import { deleteTodo } from './actions'

export function TodoList({ todos }) {
  const [optimisticTodos, removeOptimisticTodo] = useOptimistic(
    todos,
    (state, todoId) => state.filter(todo => todo.id !== todoId)
  )

  async function handleDelete(id: number) {
    removeOptimisticTodo(id) // Immediately remove from UI
    await deleteTodo(id) // Actually delete
  }

  return (
    <ul>
      {optimisticTodos.map(todo => (
        <li key={todo.id}>
          {todo.title}
          <button onClick={() => handleDelete(todo.id)}>Delete</button>
        </li>
      ))}
    </ul>
  )
}
```
