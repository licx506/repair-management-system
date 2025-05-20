FROM node:18-alpine as build

WORKDIR /app

# 复制package.json和package-lock.json
COPY frontend/package*.json ./

# 安装依赖
RUN npm ci

# 复制前端代码
COPY frontend/ .

# 构建前端，不进行类型检查
RUN npm run build

# 生产环境镜像
FROM nginx:alpine

# 复制构建产物到Nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Nginx配置通过卷挂载提供

# 暴露端口
EXPOSE 80

# 启动Nginx
CMD ["nginx", "-g", "daemon off;"]
