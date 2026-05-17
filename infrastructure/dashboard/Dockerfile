FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package.json /app/

# Install dependencies
RUN npm install

# Copy source
COPY src/ /app/src/
COPY public/ /app/public/

EXPOSE 3000

CMD ["npm", "start"]
