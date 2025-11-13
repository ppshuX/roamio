<template>
  <div class="site-footer">
    <p class="copyright">&copy; 2025 Roamio 旅行计划平台 | All Rights Reserved</p>
    <p class="beian-info">
      <a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener noreferrer">
        滇ICP备2025073012号-1
      </a>
      <span class="separator">|</span>
      <a href="http://www.beian.gov.cn/portal/registerSystemInfo?recordcode=53032202530385" target="_blank" rel="noopener noreferrer" class="gongan-beian">
        <span class="beian-icon">🛡️</span>
        滇公网安备53032202530385号
      </a>
    </p>
  </div>
</template>

<script>
export default {
  name: 'SiteFooter'
}
</script>

<style scoped>
.site-footer {
  text-align: center;
  color: #aaa;
  font-size: 0.95rem;
  margin-top: 60px;
  padding: 20px 0;
  background: transparent;
}

.site-footer .copyright {
  margin: 8px 0;
  line-height: 1.6;
}

.site-footer .beian-info {
  font-size: 0.88rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 8px;
  margin: 8px 0;
}

.site-footer .beian-info a {
  color: #999;
  text-decoration: none;
  transition: color 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.site-footer .beian-info a:hover {
  color: #667eea;
  text-decoration: underline;
}

.site-footer .beian-info .separator {
  color: #ccc;
  margin: 0 4px;
}

.site-footer .beian-info .beian-icon {
  font-size: 14px;
  vertical-align: middle;
  margin-right: 2px;
}

/* 响应式 - 移动端 */
@media (max-width: 600px) {
  .site-footer {
    font-size: 0.85rem;
    margin-top: 40px;
    padding: 15px 10px;
  }
  
  .site-footer .beian-info {
    font-size: 0.8rem;
    gap: 6px;
  }
  
  .site-footer .beian-icon {
    font-size: 12px;
  }
}
</style>

