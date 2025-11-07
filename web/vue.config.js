const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,

  // ============================================================
  // 开发服务器配置
  // ============================================================
  devServer: {
    port: 8080,
    host: '0.0.0.0',  // 允许外部访问（方便移动端调试）

    // 代理配置（开发环境跨域解决方案）
    proxy: {
      // 代理 API 请求到后端
      '^/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        ws: true,  // 支持 WebSocket
        pathRewrite: {
          // 如果需要重写路径，可以在这里配置
          // '^/api': '/api'
        }
      },
      // 代理静态文件（头像等）
      '^/static': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      // 代理媒体文件（用户上传的图片、视频）
      '^/media': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      }
    }
  },

  // ============================================================
  // 生产构建配置
  // ============================================================

  // 输出目录
  outputDir: 'dist',  // 输出到 web/dist/ 目录

  // 静态资源目录
  assetsDir: 'assets',

  // 公共路径
  // 前后端分离：前端独立部署，Nginx 直接访问 dist 目录
  publicPath: '/',

  // 生产环境的 source map（建议关闭以减小体积）
  productionSourceMap: false,

  // ============================================================
  // 性能优化
  // ============================================================

  chainWebpack: (config) => {
    // 图片压缩
    config.module
      .rule('images')
      .use('url-loader')
      .loader('url-loader')
      .tap((options) => Object.assign(options || {}, { limit: 10240 }))  // 10KB 以下转 base64

    // 代码分割
    config.optimization.splitChunks({
      chunks: 'all',
      cacheGroups: {
        // 第三方库
        vendor: {
          name: 'chunk-vendors',
          test: /[\\/]node_modules[\\/]/,
          priority: 10,
          chunks: 'initial',
        },
        // 公共代码
        common: {
          name: 'chunk-common',
          minChunks: 2,
          priority: 5,
          chunks: 'initial',
          reuseExistingChunk: true,
        },
      },
    })
  },
})
