# syntax=docker/dockerfile:1

# ==========================================================================
# Multi-stage Dockerfile for Next.js (standalone output)
# ==========================================================================
# Prerequisites:
#   next.config.js must include:  output: 'standalone'
#
# Build:
#   docker build -t myapp:latest .
#
# Run:
#   docker run -p 3000:3000 myapp:latest
# ==========================================================================

# --------------------------------------------------------------------------
# Stage 1: Install dependencies and build
# --------------------------------------------------------------------------
FROM node:20-alpine AS builder

WORKDIR /app

# Install libc6-compat for Alpine compatibility with some npm packages
RUN apk add --no-cache libc6-compat

# Copy dependency manifests first for better layer caching
COPY package.json package-lock.json* yarn.lock* pnpm-lock.yaml* ./

# Install dependencies
RUN \
    if [ -f yarn.lock ]; then yarn install --frozen-lockfile; \
    elif [ -f pnpm-lock.yaml ]; then corepack enable pnpm && pnpm install --frozen-lockfile; \
    elif [ -f package-lock.json ]; then npm ci; \
    else echo "No lockfile found." && exit 1; \
    fi

# Copy application source
COPY . .

# Build the Next.js application (standalone output)
RUN \
    if [ -f yarn.lock ]; then yarn build; \
    elif [ -f pnpm-lock.yaml ]; then corepack enable pnpm && pnpm build; \
    else npm run build; \
    fi

# --------------------------------------------------------------------------
# Stage 2: Production runtime
# --------------------------------------------------------------------------
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Create non-root user
RUN addgroup --system --gid 1001 nodejs \
    && adduser --system --uid 1001 nextjs

# Copy public assets
COPY --from=builder /app/public ./public

# Copy standalone server output
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Switch to non-root user
USER nextjs

EXPOSE 3000

CMD ["node", "server.js"]
