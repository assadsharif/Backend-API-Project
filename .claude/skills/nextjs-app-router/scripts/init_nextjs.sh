#!/usr/bin/env bash
# Initialize Next.js App Router project with best practices
#
# Usage:
#   ./init_nextjs.sh [project-name]
#
# Examples:
#   ./init_nextjs.sh my-app
#   ./init_nextjs.sh frontend

set -e

PROJECT_NAME="${1:-frontend}"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Next.js App Router Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Create Next.js app
echo -e "${GREEN}Creating Next.js app: ${PROJECT_NAME}${NC}"
npx create-next-app@latest "${PROJECT_NAME}" \
    --typescript \
    --tailwind \
    --app \
    --src-dir \
    --import-alias "@/*" \
    --use-npm

cd "${PROJECT_NAME}"

# Create lib directory with API client
echo -e "${GREEN}Creating API client...${NC}"
mkdir -p src/lib

cat > src/lib/api.ts << 'EOF'
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const api = {
  async get<T>(path: string): Promise<T> {
    const res = await fetch(`${API_BASE}${path}`)
    if (!res.ok) throw new Error(`GET ${path} failed: ${res.status}`)
    return res.json()
  },

  async post<T>(path: string, data: unknown): Promise<T> {
    const res = await fetch(`${API_BASE}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    if (!res.ok) throw new Error(`POST ${path} failed: ${res.status}`)
    return res.json()
  },

  async put<T>(path: string, data: unknown): Promise<T> {
    const res = await fetch(`${API_BASE}${path}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    if (!res.ok) throw new Error(`PUT ${path} failed: ${res.status}`)
    return res.json()
  },

  async delete(path: string): Promise<void> {
    const res = await fetch(`${API_BASE}${path}`, { method: 'DELETE' })
    if (!res.ok) throw new Error(`DELETE ${path} failed: ${res.status}`)
  }
}
EOF

# Create types directory
echo -e "${GREEN}Creating types...${NC}"
mkdir -p src/types

cat > src/types/index.ts << 'EOF'
export interface Todo {
  id: number
  title: string
  status: 'active' | 'completed'
  created_at: string
  updated_at: string
}
EOF

# Create environment files
echo -e "${GREEN}Creating environment files...${NC}"

cat > .env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF

cat > .env.example << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF

# Create loading and error components
echo -e "${GREEN}Creating loading and error components...${NC}"

cat > src/app/loading.tsx << 'EOF'
export default function Loading() {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
    </div>
  )
}
EOF

cat > src/app/error.tsx << 'EOF'
'use client'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <h2 className="text-xl font-bold mb-4">Something went wrong!</h2>
      <p className="text-gray-600 mb-4">{error.message}</p>
      <button
        onClick={reset}
        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
      >
        Try again
      </button>
    </div>
  )
}
EOF

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ Next.js project created successfully!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "Next steps:"
echo "  cd ${PROJECT_NAME}"
echo "  npm run dev"
echo ""
echo "Your app will be available at http://localhost:3000"
echo -e "${BLUE}========================================${NC}"
