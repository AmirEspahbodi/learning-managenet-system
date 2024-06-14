FROM node:20-alpine AS base

RUN mkdir /users

# Install dependencies only when needed
FROM base AS deps
# Check https://github.com/nodejs/docker-node/tree/b4117f9333da4138b03a546ec926ef50a31506c3#nodealpine to understand why libc6-compat might be needed.
RUN apk update
RUN apk add --no-cache libc6-compat
WORKDIR /users

# Install dependencies based on the preferred package manager
COPY ./users/package.json ./users/yarn.lock* ./users/package-lock.json*  ./
RUN yarn --frozen-lockfile

FROM base AS dev

WORKDIR /users
COPY --from=deps /users/node_modules ./node_modules
COPY ./users/app .
COPY ./users/public .
COPY ./users/.eslintrc.json .
COPY ./users/next.config.mjs .
COPY ./users/next-env.d.ts .
COPY ./users/postcss.config.mjs .
COPY ./users/tailwind.config.ts .
COPY ./users/tsconfig.json .

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /users
COPY --from=deps /users/node_modules ./node_modules
COPY ./users/app .
COPY ./users/public .
COPY ./users/.eslintrc.json .
COPY ./users/next.config.mjs .
COPY ./users/next-env.d.ts .
COPY ./users/postcss.config.mjs .
COPY ./users/tailwind.config.ts .
COPY ./users/tsconfig.json .

# Next.js collects completely anonymous telemetry data about general usage.
# Learn more here: https://nextjs.org/telemetry
# Uncomment the following line in case you want to disable telemetry during the build.
ENV NEXT_TELEMETRY_DISABLED 1

RUN yarn build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /users

# Uncomment the following line in case you want to disable telemetry during runtime.
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /users/public ./public

# Automatically leverage output traces to reduce image size
# https://nextjs.org/docs/advanced-features/output-file-tracing
COPY --from=builder --chown=nextjs:nodejs /users/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /users/.next/static ./.next/static

USER nextjs

CMD ["node", "server.js"]
