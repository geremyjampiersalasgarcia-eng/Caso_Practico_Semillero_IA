FROM node:20-alpine

WORKDIR /app

# Copiar archivos de dependencias
COPY package.json package-lock.json* ./

# Instalar dependencias
RUN npm ci

# Copiar código fuente
COPY . .

# Construir la app para producción
RUN npm run build

# Exponer el puerto de Next.js
EXPOSE 3000

# Comando por defecto
CMD ["npm", "start"]
