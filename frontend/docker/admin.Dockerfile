FROM node:20-alpine AS base

RUN mkdir /admin

# Install dependencies only when needed
FROM base AS deps
# Check https://github.com/nodejs/docker-node/tree/b4117f9333da4138b03a546ec926ef50a31506c3#nodealpine to understand why libc6-compat might be needed.
RUN apk update
RUN apk add --no-cache libc6-compat
WORKDIR /admin

# Install dependencies
COPY ./admin/package.json ./admin/yarn.lock* ./admin/package-lock.json* ./
RUN yarn --frozen-lockfile

FROM base AS dev

WORKDIR /admin
COPY --from=deps /admin/node_modules ./node_modules
COPY ./admin/app .
COPY ./admin/public .
COPY ./admin/.eslintrc.json .
COPY ./admin/next.config.mjs .
COPY ./admin/package.json .
COPY ./admin/postcss.config.mjs .
COPY ./admin/tailwind.config.ts .
COPY ./admin/tsconfig.json .
COPY ./admin/yarn.lock .


# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /admin
COPY --from=deps /admin/node_modules ./node_modules
COPY ./admin/app .
COPY ./admin/public .
COPY ./admin/.eslintrc.json .
COPY ./admin/next.config.mjs .
COPY ./admin/package.json .
COPY ./admin/postcss.config.mjs .
COPY ./admin/tailwind.config.ts .
COPY ./admin/tsconfig.json .
COPY ./admin/yarn.lock .


# Next.js collects completely anonymous telemetry data about general usage.
# Learn more here: https://nextjs.org/telemetry
# Uncomment the following line in case you want to disable telemetry during the build.
ENV NEXT_TELEMETRY_DISABLED 1

RUN yarn build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /admin

# Uncomment the following line in case you want to disable telemetry during runtime.
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /admin/public ./public

# Automatically leverage output traces to reduce image size
# https://nextjs.org/docs/advanced-features/output-file-tracing
COPY --from=builder --chown=nextjs:nodejs /admin/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /admin/.next/static ./.next/static

USER nextjs

CMD ["node", "server.js"]
