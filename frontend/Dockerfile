FROM node:20-alpine

WORKDIR /app

# Copy package manifests terlebih dahulu untuk cache layer
COPY package*.json ./

# Install deps (jika package.json belum ada, step ini akan gagal; jalankan init Next.js lebih dulu)
RUN npm install

# Copy seluruh source
COPY . .

# Expose & run dev
EXPOSE 3000
CMD ["npm", "run", "dev"]
