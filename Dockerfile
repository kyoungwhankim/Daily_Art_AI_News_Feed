FROM nginx:alpine
COPY index.html app.css app.jsx articles.js /usr/share/nginx/html/
EXPOSE 80
