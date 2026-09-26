<template>
  <div class="report">
    <el-card>
      <div class="report-header">
        <h2>扫描报告</h2>
        <div>
          <el-button @click="downloadReport('html')">下载HTML</el-button>
          <el-button @click="downloadReport('markdown')">下载Markdown</el-button>
          <el-button @click="$router.back()">返回</el-button>
        </div>
      </div>
      
      <el-descriptions :column="2" border class="report-info">
        <el-descriptions-item label="扫描ID">{{ report.scan_id }}</el-descriptions-item>
        <el-descriptions-item label="目标URL">{{ report.target_url }}</el-descriptions-item>
        <el-descriptions-item label="开始时间">{{ report.start_time }}</el-descriptions-item>
        <el-descriptions-item label="结束时间">{{ report.end_time || '进行中' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(report.status)">
            {{ report.status }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="漏洞数量">{{ report.vulnerabilities?.length || 0 }}</el-descriptions-item>
      </el-descriptions>
      
      <h3 style="margin-top: 30px;">漏洞列表</h3>
      
      <el-table :data="report.vulnerabilities || []" style="width: 100%">
        <el-table-column prop="severity" label="严重程度" width="100">
          <template #default="{ row }">
            <el-tag :type="getSeverityType(row.severity)">
              {{ row.severity }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="漏洞名称" />
        <el-table-column prop="location" label="位置" width="250" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button size="small" @click="viewDetail(row)">详情</el-button>
            <el-button size="small" @click="executePoc(row)">执行POC</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 漏洞详情对话框 -->
    <el-dialog v-model="detailVisible" title="漏洞详情" width="70%">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="漏洞名称">{{ currentVuln.name }}</el-descriptions-item>
        <el-descriptions-item label="严重程度">
          <el-tag :type="getSeverityType(currentVuln.severity)">
            {{ currentVuln.severity }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="描述">{{ currentVuln.description }}</el-descriptions-item>
        <el-descriptions-item label="位置">{{ currentVuln.location }}</el-descriptions-item>
        <el-descriptions-item label="修复建议">{{ currentVuln.remediation }}</el-descriptions-item>
        <el-descriptions-item label="POC">
          <pre>{{ currentVuln.poc }}</pre>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const route = useRoute()
const report = ref({})
const detailVisible = ref(false)
const currentVuln = ref({})

const getStatusType = (status) => {
  const types = {
    'running': '',
    'completed': 'success',
    'failed': 'danger',
    'stopped': 'warning'
  }
  return types[status] || ''
}

const getSeverityType = (severity) => {
  const types = {
    '高': 'danger',
    '中': 'warning',
    '低': 'info'
  }
  return types[severity] || ''
}

const loadReport = async () => {
  try {
    const scanId = route.params.scanId
    const response = await axios.get(`/api/report/${scanId}`)
    report.value = response.data
  } catch (error) {
    ElMessage.error('加载报告失败')
  }
}

const viewDetail = (vuln) => {
  currentVuln.value = vuln
  detailVisible.value = true
}

const executePoc = (vuln) => {
  // TODO: 实现POC执行逻辑
  ElMessage.info('POC执行功能待实现')
}

const downloadReport = (format) => {
  // TODO: 实现报告下载逻辑
  ElMessage.info(`下载${format}报告功能待实现`)
}

onMounted(() => {
  loadReport()
})
</script>

<style scoped>
.report {
  padding: 20px;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.report-info {
  margin-top: 20px;
}

pre {
  background-color: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
}
</style>
