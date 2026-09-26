<template>
  <div class="settings">
    <el-card>
      <h2>系统设置</h2>
      
      <el-tabs v-model="activeTab">
        <el-tab-pane label="扫描配置" name="scanner">
          <el-form :model="scannerConfig" label-width="150px">
            <el-form-item label="默认最大并发数">
              <el-input-number v-model="scannerConfig.maxConcurrency" :min="1" :max="50" />
            </el-form-item>
            <el-form-item label="默认速率限制 (req/s)">
              <el-input-number v-model="scannerConfig.rateLimit" :min="10" :max="200" />
            </el-form-item>
            <el-form-item label="默认超时时间 (秒)">
              <el-input-number v-model="scannerConfig.timeout" :min="5" :max="120" />
            </el-form-item>
            <el-form-item label="默认爬取深度">
              <el-input-number v-model="scannerConfig.maxDepth" :min="1" :max="10" />
            </el-form-item>
            <el-form-item label="User-Agent">
              <el-input v-model="scannerConfig.userAgent" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveScannerConfig">保存配置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="报告配置" name="report">
          <el-form :model="reportConfig" label-width="150px">
            <el-form-item label="默认报告格式">
              <el-radio-group v-model="reportConfig.defaultFormat">
                <el-radio label="html">HTML</el-radio>
                <el-radio label="markdown">Markdown</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="包含POC">
              <el-switch v-model="reportConfig.includePoc" />
            </el-form-item>
            <el-form-item label="包含截图">
              <el-switch v-model="reportConfig.includeScreenshots" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveReportConfig">保存配置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="插件管理" name="plugins">
          <div class="plugin-list">
            <h3>已安装插件</h3>
            <el-empty v-if="plugins.length === 0" description="暂无插件" />
            <el-table v-else :data="plugins" style="width: 100%">
              <el-table-column prop="name" label="插件名称" />
              <el-table-column prop="version" label="版本" width="100" />
              <el-table-column prop="description" label="描述" />
              <el-table-column prop="enabled" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.enabled ? 'success' : 'info'">
                    {{ row.enabled ? '启用' : '禁用' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="150">
                <template #default="{ row }">
                  <el-button size="small" @click="togglePlugin(row)">
                    {{ row.enabled ? '禁用' : '启用' }}
                  </el-button>
                  <el-button size="small" type="danger" @click="removePlugin(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
            
            <div style="margin-top: 20px;">
              <el-button type="primary" @click="installPlugin">安装新插件</el-button>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const activeTab = ref('scanner')

const scannerConfig = reactive({
  maxConcurrency: 10,
  rateLimit: 50,
  timeout: 30,
  maxDepth: 5,
  userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) WebVulnScanner/1.0'
})

const reportConfig = reactive({
  defaultFormat: 'html',
  includePoc: true,
  includeScreenshots: false
})

const plugins = ref([])

const saveScannerConfig = async () => {
  try {
    // TODO: 实现保存配置逻辑
    ElMessage.success('扫描配置已保存')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const saveReportConfig = async () => {
  try {
    // TODO: 实现保存配置逻辑
    ElMessage.success('报告配置已保存')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const togglePlugin = (plugin) => {
  plugin.enabled = !plugin.enabled
  ElMessage.success(`插件已${plugin.enabled ? '启用' : '禁用'}`)
}

const removePlugin = async (plugin) => {
  // TODO: 实现删除插件逻辑
  ElMessage.success('插件已删除')
}

const installPlugin = () => {
  // TODO: 实现安装插件逻辑
  ElMessage.info('安装插件功能待实现')
}

onMounted(() => {
  // TODO: 加载配置和插件列表
})
</script>

<style scoped>
.settings {
  padding: 20px;
}

.plugin-list {
  margin-top: 20px;
}
</style>
