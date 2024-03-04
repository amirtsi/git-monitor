FROM node:16-alpine3.11   
# Set the working directory inside the image
WORKDIR /app

# Copy the contents of the local project directory into the image at /app
COPY . .

# Install dependencies
RUN npm install 
RUN mkdir -p node_modules/.cache && chmod -R 777 node_modules
USER node

# Expose port 3000 to the Docker host, so we can access it
EXPOSE 3000

# Run the npm start command when the container launches
CMD ["npm", "start"]
