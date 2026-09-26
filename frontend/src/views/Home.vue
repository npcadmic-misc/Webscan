<template>
  <div class="home">
    <el-card class="welcome-card">
      <h2>欢迎使用Web漏洞扫描系统</h2>
      <p>一个功能完整的Web应用程序漏洞扫描工具</p>
      
      <el-row :gutter="20" class="feature-list">
        <el-col :span="8">
          <el-card shadow="hover">
            <el-icon :size="40"><Search /></el-icon>
            <h3>多种扫描类型</h3>
            <p>支持基础扫描、深度扫描和API扫描</p>
          </el-card>
        </el-col>
        
        <el-col :span="8">
          <el-card shadow="hover">
            <el-icon :size="40"><Document /></el-icon>
            <h3>报告生成</h3>
            <p>支持HTML和Markdown格式报告</p>
          </el-card>
        </el-col>
        
        <el-col :span="8">
          <el-card shadow="hover">
            <el-icon :size="40"><Tools /></el-icon>
            <h3>插件系统</h3>
            <p>支持自定义扫描模块和规则</p>
          </el-card>
        </el-col>
      </el-row>
      
      <div class="action-buttons">
        <el-button type="primary" size="large" @click="$router.push('/scan')">
          开始扫描
        </el-button>
        <el-button size="large" @click="$router.push('/history')">
          查看历史
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { Search, Document, Tools } from '@element-plus/icons-vue'
</script>

<style scoped>
.home {
  padding: 20px;
}

.welcome-card {
  max-width: 1200px;
  margin: 0 auto;
}

.feature-list {
  margin-top: 30px;
}

.feature-list .el-card {
  text-align: center;
  padding: 20px;
}

.feature-list h3 {
  margin: 15px 0 10px;
}

.action-buttons {
  margin-top: 40px;
  text-align: center;
}

.action-buttons .el-button {
  margin: 0 10px;
}
</style>
