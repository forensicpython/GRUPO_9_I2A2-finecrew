const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  // Proxy específico para downloads
  app.use(
    '/api/download',
    createProxyMiddleware({
      target: 'http://localhost:5001',
      changeOrigin: true,
      timeout: 300000, // 5 minutos para downloads
      proxyTimeout: 300000,
      logLevel: 'info',
      onError: (err, req, res) => {
        console.error('Download Proxy Error:', err);
        res.status(500).json({ 
          error: `Erro no download: ${err.message}`,
          details: 'Verifique se o backend está rodando na porta 5001'
        });
      },
      onProxyReq: (proxyReq, req, res) => {
        console.log(`📥 Download Request: ${req.method} ${req.url}`);
        // Headers específicos para download
        proxyReq.setHeader('Accept', 'application/octet-stream, */*');
      },
      onProxyRes: (proxyRes, req, res) => {
        console.log(`📤 Download Response: ${proxyRes.statusCode} for ${req.url}`);
        // Garantir headers de download
        if (proxyRes.statusCode === 200) {
          const filename = req.url.split('/').pop();
          proxyRes.headers['content-disposition'] = `attachment; filename="${filename}"`;
          proxyRes.headers['cache-control'] = 'no-cache, no-store, must-revalidate';
        }
      }
    })
  );

  // Proxy geral para outras rotas da API
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://localhost:5001',
      changeOrigin: true,
      timeout: 600000, // 10 minutos
      proxyTimeout: 600000, // 10 minutos
      logLevel: 'info',
      onError: (err, req, res) => {
        console.error('API Proxy Error:', err);
        res.status(500).json({ 
          error: `Proxy Error: ${err.message}`,
          details: 'Verifique se o backend está rodando na porta 5001'
        });
      },
      onProxyReq: (proxyReq, req, res) => {
        console.log(`🔄 API Request: ${req.method} ${req.url}`);
      },
      onProxyRes: (proxyRes, req, res) => {
        console.log(`✅ API Response: ${proxyRes.statusCode} for ${req.url}`);
      }
    })
  );
};