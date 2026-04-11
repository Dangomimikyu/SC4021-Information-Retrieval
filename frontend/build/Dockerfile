# Step 1: Use a lightweight Node.js image as the base
FROM node:20-alpine

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy dependency files first to leverage Docker cache
COPY package*.json ./
# Copy yarn.lock if you are using yarn, otherwise it will be ignored
COPY yarn.lock* ./ 

# Step 4: Install dependencies inside the container
RUN npm install

# Step 5: Copy all frontend source code into the container
# Note: This will copy files from the 'frontend' folder as defined in docker-compose context
COPY . .

# Step 6: Expose the port that the Vite dev server runs on
EXPOSE 5173

# Step 7: Start the development server
# --host 0.0.0.0 is mandatory to allow access from outside the container
# --port 5173 ensures it matches the exposed port
CMD ["npm", "run", "dev", "--", "--host"]