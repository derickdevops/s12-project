FROM node:24-alpine

ENV NODE_ENV=production

WORKDIR /usr/src/app

COPY app/package*.json ./
RUN npm install --omit=dev

COPY app/ ./

EXPOSE 3000

USER node

CMD ["node", "server.js"]
