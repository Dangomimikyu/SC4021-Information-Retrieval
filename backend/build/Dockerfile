FROM node:20-alpine

WORKDIR /app

# Copy các file định nghĩa thư viện
COPY package*.json ./
COPY tsconfig.json ./

# Cài đặt thư viện (bao gồm cả các gói @types)
RUN npm install

# Copy toàn bộ code
COPY . .

# Chỉ chạy tsc một lần với các cờ bỏ qua kiểm tra thư viện để tránh lỗi vặt
RUN npx tsc --skipLibCheck

EXPOSE 8000

# Chạy file index.js nằm trong thư mục dist (theo outDir trong tsconfig)
CMD ["node", "dist/index.js"]