FROM node:22-alpine AS deps
WORKDIR /app/governance-console/frontend
COPY governance-console/frontend/package.json governance-console/frontend/package-lock.json ./
RUN npm ci

FROM node:22-alpine AS builder
WORKDIR /app/governance-console/frontend
COPY packages/ui-tokens /app/packages/ui-tokens
COPY assets/noetfield-tokens.css /app/assets/noetfield-tokens.css
COPY --from=deps /app/governance-console/frontend/node_modules ./node_modules
COPY governance-console/frontend .
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
RUN npm run build

FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME=0.0.0.0

RUN addgroup --system --gid 1001 nodejs && adduser --system --uid 1001 nextjs

COPY --from=builder --chown=nextjs:nodejs /app/governance-console/frontend/.next/standalone/governance-console/frontend ./

USER nextjs
EXPOSE 3000

CMD ["node", "server.js"]
