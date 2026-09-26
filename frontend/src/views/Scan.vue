<template>
  <div class="scan">
    <el-card>
      <h2>新建扫描任务</h2>
      
      <el-form :model="form" label-width="120px" class="scan-form">
        <el-form-item label="目标URL" required>
          <el-input v-model="form.targetUrl" placeholder="https://example.com" />
        </el-form-item>
        
        <el-form-item label="扫描类型">
          <el-checkbox-group v-model="form.scanTypes">
            <el-checkbox label="basic">基础扫描 (OWASP Top 10)</el-checkbox>
            <el-checkbox label="deep">深度扫描 (越权、业务逻辑)</el-checkbox>
            <el-checkbox label="api">API扫描 (REST/GraphQL)</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        
        <el-form-item label="认证配置">
          <el-switch v-model="form.useAuth" />
          <div v-if="form.useAuth" class="auth-config">
            <el-select v-model="form.authType" style="width: 150px;">
              <el-option label="Cookie" value="cookie" />
              <el-option label="Token" value="token" />
              <el-option label="Bearer" value="bearer" />
            </el-select>
            <el-input 
              v-model="form.authValue" 
              placeholder="输入认证值"
              style="margin-left: 10px; width: 400px;"
            />
          </div>
        </el-form-item>
        
        <el-form-item label="高级配置">
          <el-collapse>
            <el-collapse-item title="性能配置" name="1">
              <el-form-item label="最大并发数">
                <el-slider v-model="form.maxConcurrency" :min="1" :max="50" />
              </el-form-item>
              <el-form-item label="速率限制 (req/s)">
                <el-slider v-model="form.rateLimit" :min="10" :max="200" />
              </el-form-item>
              <el-form-item label="超时时间 (秒)">
                <el-input-number v-model="form.timeout" :min="5" :max="120" />
              </el-form-item>
            </el-collapse-item>
            
            <el-collapse-item title="扫描范围" name="2">
              <el-form-item label="最大爬取深度">
                <el-input-number v-model="form.maxDepth" :min="1" :max="10" />
              </el-form-item>
              <el-form-item label="排除路径">
                <el-input 
                  v-model="form.excludedPaths" 
                  type="textarea"
                  placeholder="每行一个路径，如 /admin, /logout"
                />
              </el-form-item>
            </el-collapse-item>
          </el-collapse>
        </el-form-item>
        
        <el-form-item label="报告格式">
          <el-radio-group v-model="form.reportFormat">
            <el-radio label="html">HTML</el-radio>
            <el-radio label="markdown">Markdown</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="startScan" :loading="scanning">
            开始扫描
          </el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 扫描进度 -->
    <el-card v-if="scanning" class="progress-card">
      <h3>扫描进度</h3>
      <el-progress :percentage="progress" :status="progressStatus" />
      <p>{{ progressMessage }}</p>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const form = reactive({
  targetUrl: '',
  scanTypes: ['basic', 'deep', 'api'],
  useAuth: false,
  authType: 'cookie',
  authValue: '',
  maxConcurrency: 10,
  rateLimit: 50,
  timeout: 30,
  maxDepth: 5,
  excludedPaths: '',
  reportFormat: 'html'
})

const scanning = ref(false)
const progress = ref(0)
const progressStatus = ref('')
const progressMessage = ref('准备中...')

const startScan = async () => {
  if (!form.targetUrl) {
    ElMessage.error('请输入目标URL')
    return
  }
  
  scanning.value = true
  progress.value = 0
  progressMessage.value = '正在启动扫描...'
  
  try {
    const config = {
      target_url: form.targetUrl,
      scan_types: form.scanTypes,
      max_concurrency: form.maxConcurrency,
      rate_limit: form.rateLimit,
      timeout: form.timeout,
      max_depth: form.maxDepth,
      excluded_paths: form.excludedPaths.split('\n').filter(p => p.trim()),
      auth_config: form.useAuth ? {
        type: form.authType,
        value: form.authValue
      } : null
    }
    
    const response = await axios.post('/api/scan/start', config)
    
    ElMessage.success(`扫描任务已创建，ID: ${response.data.scan_id}`)
    
    // TODO: 实现实时进度监控
    
  } catch (error) {
    ElMessage.error('启动扫描失败: ' + error.message)
  } finally {
    scanning.value = false
  }
}

const resetForm = () => {
  form.targetUrl = ''
  form.scanTypes = ['basic', 'deep', 'api']
  form.useAuth = false
  form.authValue = ''
  form.maxConcurrency = 10
  form.rateLimit = 50
  form.timeout = 30
  form.maxDepth = 5
  form.excludedPaths = ''
  form.reportFormat = 'html'
}
</script>

<style scoped>
.scan {
  padding: 20px;
}

.scan-form {
  max-width: 800px;
}

.auth-config {
  margin-top: 10px;
}

.progress-card {
  margin-top: 20px;
}
</style>
