<template>
  <div class="history">
    <el-card>
      <h2>扫描历史</h2>
      
      <el-table :data="historyList" style="width: 100%">
        <el-table-column prop="scan_id" label="扫描ID" width="250" />
        <el-table-column prop="target_url" label="目标URL" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="viewReport(row.scan_id)">
              查看报告
            </el-button>
            <el-button size="small" type="danger" @click="deleteScan(row.scan_id)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-empty v-if="historyList.length === 0" description="暂无扫描历史" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const historyList = ref([])

const getStatusType = (status) => {
  const types = {
    'running': '',
    'completed': 'success',
    'failed': 'danger',
    'stopped': 'warning'
  }
  return types[status] || ''
}

const loadHistory = async () => {
  try {
    const response = await axios.get('/api/scan/history')
    historyList.value = response.data
  } catch (error) {
    ElMessage.error('加载历史记录失败')
  }
}

const viewReport = (scanId) => {
  router.push(`/report/${scanId}`)
}

const deleteScan = async (scanId) => {
  try {
    await ElMessageBox.confirm('确定要删除这条扫描记录吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    // TODO: 实现删除逻辑
    ElMessage.success('删除成功')
    loadHistory()
  } catch {
    // 用户取消
  }
}

onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
.history {
  padding: 20px;
}
</style>
