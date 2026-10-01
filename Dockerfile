FROM nginx:alpine
COPY index.html app.css app.jsx config.js /usr/share/nginx/html/
COPY data /usr/share/nginx/html/data
EXPOSE 80
