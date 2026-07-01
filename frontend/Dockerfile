FROM node:24-alpine

WORKDIR /app

RUN corepack enable

COPY package.json pnpm-lock.yaml* pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile

COPY index.html vite.config.ts tsconfig.json tsconfig.node.json ./
COPY src ./src

EXPOSE 5173

CMD ["pnpm", "dev", "--host", "0.0.0.0"]
