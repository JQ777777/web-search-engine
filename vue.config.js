const { defineConfig } = require('@vue/cli-service');

module.exports = defineConfig({
  // 设置 publicPath 为 '/'
  publicPath: '/',

  // 开发服务器配置
  devServer: {
    proxy: {
      '/api': {
        target: 'http://localhost:9200',
        changeOrigin: true,
        pathRewrite: { '^/api': '' },
      },
    },
  },
});