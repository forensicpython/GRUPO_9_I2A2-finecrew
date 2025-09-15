const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://localhost:5001',
      changeOrigin: true,
      timeout: 600000, // 10 minutos
      proxyTimeout: 600000, // 10 minutos
      logLevel: 'debug',
      onError: (err, req, res) => {
        console.error('Proxy Error:', err);
        res.status(500).json({ 
          error: `Proxy Error: ${err.message}`,
          details: 'Verifique se o backend está rodando na porta 5001'
        });
      },
      onProxyReq: (proxyReq, req, res) => {
        console.log(`Proxy Request: ${req.method} ${req.url}`);
      },
      onProxyRes: (proxyRes, req, res) => {
        console.log(`Proxy Response: ${proxyRes.statusCode} for ${req.url}`);
      }
    })
  );
};