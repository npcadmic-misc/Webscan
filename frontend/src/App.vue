<template>
  <el-container class="app-container">
    <el-header class="app-header">
      <h1>Web漏洞扫描系统</h1>
    </el-header>
    
    <el-main>
      <router-view />
    </el-main>
    
    <el-footer class="app-footer">
      <p>© 2024 Web漏洞扫描系统 v1.0.0</p>
    </el-footer>
  </el-container>
</template>

<script setup>
// App组件
</script>

<style scoped>
.app-container {
  height: 100vh;
}

.app-header {
  background-color: #409eff;
  color: white;
  display: flex;
  align-items: center;
}

.app-header h1 {
  margin: 0;
  font-size: 24px;
}

.app-footer {
  text-align: center;
  padding: 10px;
  background-color: #f5f7fa;
}
</style>
