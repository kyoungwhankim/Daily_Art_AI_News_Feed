FROM nginx:alpine
COPY index.html app.css app.jsx articles.js whitelist.js /usr/share/nginx/html/
EXPOSE 80
