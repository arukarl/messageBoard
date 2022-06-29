FROM node:slim

# Create app directory
WORKDIR /usr/src/app

COPY package*.json ./

RUN npm install -g npm@8.13.1

RUN npm ci --omit=dev

COPY . .

EXPOSE 3000

CMD [ "npm", "run" , "serve"]