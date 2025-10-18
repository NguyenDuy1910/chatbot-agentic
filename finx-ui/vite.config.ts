import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'node:path'
import { fileURLToPath } from 'node:url';

// Plugin để log page requests và client navigation
const pageLoggerPlugin = () => {
  return {
    name: 'page-logger',
    configureServer(server: any) {
      server.middlewares.use((req: any, res: any, next: any) => {
        const timestamp = new Date().toLocaleTimeString();
        const method = req.method;
        const url = req.url;

        // Handle client-side navigation logs
        if (method === 'POST' && url === '/dev-log') {
          let body = '';
          req.on('data', (chunk: any) => {
            body += chunk.toString();
          });
          req.on('end', () => {
            try {
              const logData = JSON.parse(body);
              console.log(`\x1b[36m[${logData.timestamp}]\x1b[0m \x1b[35m[CLIENT]\x1b[0m \x1b[32m${logData.method}\x1b[0m \x1b[33m${logData.url}\x1b[0m \x1b[32m200 OK\x1b[0m`);
            } catch (e) {
              // Ignore parsing errors
            }
          });
          res.writeHead(200, { 'Content-Type': 'application/json' });
          res.end('{"status":"ok"}');
          return;
        }

        // Log server requests (page loads, refreshes)
        if (method === 'GET' && !url.includes('.') && !url.startsWith('/@') && !url.startsWith('/node_modules') && url !== '/dev-log') {
          console.log(`\x1b[36m[${timestamp}]\x1b[0m \x1b[34m[SERVER]\x1b[0m \x1b[32mGET\x1b[0m \x1b[33mhttp://localhost:3000${url}\x1b[0m \x1b[32m200 OK\x1b[0m`);
        }

        next();
      });
    }
  };
};

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), pageLoggerPlugin()],
  resolve: {
    alias: {
      "@": path.resolve(path.dirname(fileURLToPath(import.meta.url)), './src'),
      "./react": "react"
    },
  },
  server: {
    port: 3000
  }
})
