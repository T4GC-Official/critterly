# Use the official Node.js image as a base
FROM node:16-slim

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json (if available)
COPY package.json /app

# Install the dependencies
RUN npm install

# Copy the rest of the application source code
COPY . /app

# Expose port 8080 for the dev server
EXPOSE 8080

# Command to run the Vue development server
CMD ["npm", "run", "serve"]

