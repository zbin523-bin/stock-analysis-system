FROM node:18-alpine

WORKDIR /app

# 6package.jsonŒpackage-lock.json
COPY package*.json ./

# ‰ÅV
RUN npm ci --only=production

# 6Y‡ö
COPY ../web/static ./static
COPY ../web/index.html ./index.html

# ú€U„HTTP¡h
RUN echo 'const http = require("http"); const fs = require("fs"); const path = require("path"); const url = require("url"); const server = http.createServer((req, res) => { const pathname = url.parse(req.url).pathname; let filePath = pathname === "/" ? "/index.html" : pathname; filePath = path.join(__dirname, filePath); const extname = path.extname(filePath); let contentType = "text/html"; switch(extname) { case ".js": contentType = "application/javascript"; break; case ".css": contentType = "text/css"; break; case ".json": contentType = "application/json"; break; case ".png": contentType = "image/png"; break; case ".jpg": contentType = "image/jpg"; break; } fs.readFile(filePath, (err, content) => { if (err) { res.writeHead(404); res.end("File not found"); } else { res.writeHead(200, { "Content-Type": contentType }); res.end(content, "utf-8"); } }); }); server.listen(8080, () => { console.log("Frontend server running on port 8080"); });' > server.js

EXPOSE 8080

CMD ["node", "server.js"]