FROM node:22-slim AS build
RUN apt-get update && apt-get install -y python3 make g++ && rm -rf /var/lib/apt/lists/*
WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:22-slim
RUN apt-get update && apt-get install -y git jq curl python3 make g++ && rm -rf /var/lib/apt/lists/*
# Install uv for Python tooling (web-fetch, research-memory, enrichment)
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin:${PATH}"
WORKDIR /app

COPY package*.json ./
RUN npm ci --omit=dev

COPY --from=build /app/dist ./dist
COPY --from=build /app/skills ./skills
COPY scripts/ ./scripts/
COPY prompts/ ./prompts/
# Tool-tied skills for agent use
COPY .skills/web-fetch/SKILL.md ./skills/web-fetch/SKILL.md
COPY .skills/research-memory/SKILL.md ./skills/research-memory/SKILL.md

ENV NODE_ENV=production
EXPOSE 9090

CMD ["node", "dist/main.js"]
