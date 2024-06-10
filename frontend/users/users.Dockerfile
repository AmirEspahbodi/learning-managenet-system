FROM node:20-alpine as build

RUN mkdir frontend

WORKDIR /frontend

COPY . .

COPY ./package.json ./package-lock.json ./

RUN npm install

# Expose port 80
EXPOSE 80

# Start the Vite development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5002"]