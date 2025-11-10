<template>
  <v-container fluid class="pa-6">
    <v-card elevation="2" rounded="lg" class="directory-card">
      <!-- 头部工具栏 -->
      <v-card-title class="d-flex align-center pa-4 bg-primary">
        <v-icon size="28" class="mr-3">mdi-folder-open</v-icon>
        <span class="text-h5 font-weight-bold">文件目录</span>
        <v-spacer></v-spacer>
        <v-chip color="white" variant="outlined" size="small"> {{ items.length }} 项 </v-chip>
      </v-card-title>

      <v-divider></v-divider>

      <!-- 视图切换按钮 -->
      <v-card-text class="pa-4 scrollable-content">
        <div class="d-flex align-center mb-4">
          <v-btn-toggle v-model="viewMode" mandatory color="primary" variant="outlined" divided>
            <v-btn value="list" size="small">
              <v-icon>mdi-view-list</v-icon>
              <span class="ml-2">列表</span>
            </v-btn>
            <v-btn value="grid" size="small">
              <v-icon>mdi-view-grid</v-icon>
              <span class="ml-2">网格</span>
            </v-btn>
          </v-btn-toggle>

          <v-spacer></v-spacer>

          <!-- 搜索框 -->
          <v-text-field
            v-model="searchQuery"
            prepend-inner-icon="mdi-magnify"
            label="搜索文件"
            variant="outlined"
            density="compact"
            hide-details
            clearable
            style="max-width: 300px"
          ></v-text-field>
        </div>

        <!-- 列表视图 -->
        <v-list v-if="viewMode === 'list'" class="pa-0" lines="two">
          <v-list-item
            v-for="(item, index) in filteredItems"
            :key="index"
            :ripple="true"
            class="file-item px-4 py-2"
            @click="handleItemClick(item)"
          >
            <template v-slot:prepend>
              <v-avatar :color="getItemColor(item)" size="48" class="mr-3">
                <v-icon :icon="getItemIcon(item)" size="28" color="white"></v-icon>
              </v-avatar>
            </template>

            <v-list-item-title class="text-subtitle-1 font-weight-medium">
              {{ item.file_name }}
              <v-chip
                v-if="item.file_type === 'link'"
                size="x-small"
                color="info"
                variant="tonal"
                class="ml-2"
              >
                链接
              </v-chip>
            </v-list-item-title>

            <v-list-item-subtitle class="text-caption">
              <div class="d-flex align-center mt-1">
                <span class="mr-3">{{ item.full_name }}</span>
                <v-divider vertical class="mx-2"></v-divider>
                <span v-if="item.file_type !== 'directory'">{{ formatSize(item.size) }}</span>
                <span v-else class="text-grey">文件夹</span>
                <span v-if="item.target" class="ml-3 text-info">
                  <v-icon size="14" class="mr-1">mdi-arrow-right</v-icon>
                  {{ item.target }}
                </span>
              </div>
            </v-list-item-subtitle>

            <template v-slot:append>
              <v-menu>
                <template v-slot:activator="{ props }">
                  <v-btn
                    icon="mdi-dots-vertical"
                    variant="text"
                    size="small"
                    v-bind="props"
                  ></v-btn>
                </template>
                <v-list density="compact">
                  <v-list-item @click="() => {}">
                    <template v-slot:prepend>
                      <v-icon>mdi-information</v-icon>
                    </template>
                    <v-list-item-title>详情</v-list-item-title>
                  </v-list-item>
                  <v-list-item @click="() => {}">
                    <template v-slot:prepend>
                      <v-icon>mdi-share-variant</v-icon>
                    </template>
                    <v-list-item-title>分享</v-list-item-title>
                  </v-list-item>
                </v-list>
              </v-menu>
            </template>
          </v-list-item>
        </v-list>

        <!-- 网格视图 -->
        <v-row v-else dense>
          <v-col v-for="(item, index) in filteredItems" :key="index" cols="12" sm="6" md="4" lg="3">
            <v-card
              class="file-card"
              elevation="2"
              :ripple="true"
              @click="handleItemClick(item)"
              hover
            >
              <div class="d-flex flex-column align-center pa-4">
                <v-avatar :color="getItemColor(item)" size="80" class="mb-3">
                  <v-icon :icon="getItemIcon(item)" size="48" color="white"></v-icon>
                </v-avatar>

                <v-card-title
                  class="text-center text-body-1 px-2 pb-1"
                  style="word-break: break-word"
                >
                  {{ item.file_name }}
                </v-card-title>

                <v-card-subtitle class="text-center text-caption px-2">
                  <v-chip
                    v-if="item.file_type === 'link'"
                    size="x-small"
                    color="info"
                    variant="tonal"
                    class="mb-2"
                  >
                    链接
                  </v-chip>
                  <div>
                    {{ item.file_type !== 'directory' ? formatSize(item.size) : '文件夹' }}
                  </div>
                  <div v-if="item.target" class="text-info mt-1">
                    <v-icon size="12">mdi-arrow-right</v-icon>
                    {{ truncateText(item.target, 20) }}
                  </div>
                </v-card-subtitle>
              </div>

              <v-divider></v-divider>

              <v-card-actions class="justify-center">
                <v-btn size="small" variant="text" color="primary" @click.stop="() => {}">
                  <v-icon size="18" class="mr-1">mdi-information</v-icon>
                  详情
                </v-btn>
              </v-card-actions>
            </v-card>
          </v-col>
        </v-row>

        <!-- 空状态 -->
        <div v-if="filteredItems.length === 0" class="text-center py-12">
          <v-avatar color="grey-lighten-2" size="120" class="mb-4">
            <v-icon size="60" color="grey">mdi-folder-open-outline</v-icon>
          </v-avatar>
          <div class="text-h6 text-grey mb-2">
            {{ searchQuery ? '未找到匹配的文件' : '目录为空' }}
          </div>
          <div class="text-caption text-grey">
            {{ searchQuery ? '尝试使用其他关键词搜索' : '暂无文件或文件夹' }}
          </div>
        </div>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, computed } from 'vue'

// Props
const props = defineProps({
  items: {
    type: Array,
    default: () => [],
    // 数组元素格式: { file_name, full_name, file_type, size, target }
  },
})

// Emit
const emit = defineEmits(['item-click'])

// 数据
const viewMode = ref('list') // 'list' 或 'grid'
const searchQuery = ref('')

// 过滤后的项目
const filteredItems = computed(() => {
  if (!searchQuery.value) {
    return props.items
  }
  const query = searchQuery.value.toLowerCase()
  return props.items.filter(
    (item) =>
      item.file_name.toLowerCase().includes(query) || item.full_name.toLowerCase().includes(query),
  )
})

// 获取图标
const getItemIcon = (item) => {
  switch (item.file_type) {
    case 'directory':
      return 'mdi-folder'
    case 'link':
      return 'mdi-link-variant'
    case 'file':
      // 根据文件扩展名返回不同图标
      const ext = item.file_name.split('.').pop()?.toLowerCase()
      const iconMap = {
        pdf: 'mdi-file-pdf-box',
        doc: 'mdi-file-word',
        docx: 'mdi-file-word',
        xls: 'mdi-file-excel',
        xlsx: 'mdi-file-excel',
        ppt: 'mdi-file-powerpoint',
        pptx: 'mdi-file-powerpoint',
        jpg: 'mdi-file-image',
        jpeg: 'mdi-file-image',
        png: 'mdi-file-image',
        gif: 'mdi-file-image',
        mp4: 'mdi-file-video',
        avi: 'mdi-file-video',
        mp3: 'mdi-file-music',
        wav: 'mdi-file-music',
        zip: 'mdi-folder-zip',
        rar: 'mdi-folder-zip',
        txt: 'mdi-file-document',
        js: 'mdi-language-javascript',
        py: 'mdi-language-python',
        java: 'mdi-language-java',
        html: 'mdi-language-html5',
        css: 'mdi-language-css3',
      }
      return iconMap[ext] || 'mdi-file'
    default:
      return 'mdi-file'
  }
}

// 获取颜色
const getItemColor = (item) => {
  switch (item.file_type) {
    case 'directory':
      return 'amber'
    case 'link':
      return 'cyan'
    case 'file':
      const ext = item.file_name.split('.').pop()?.toLowerCase()
      const colorMap = {
        pdf: 'red',
        doc: 'blue',
        docx: 'blue',
        xls: 'green',
        xlsx: 'green',
        ppt: 'orange',
        pptx: 'orange',
        jpg: 'purple',
        jpeg: 'purple',
        png: 'purple',
        gif: 'purple',
        mp4: 'pink',
        mp3: 'teal',
        zip: 'brown',
        txt: 'grey',
        js: 'yellow',
        py: 'blue-grey',
        html: 'deep-orange',
      }
      return colorMap[ext] || 'blue-grey'
    default:
      return 'grey'
  }
}

// 格式化文件大小
const formatSize = (bytes) => {
  if (!bytes || bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

// 截断文本
const truncateText = (text, maxLength) => {
  if (!text || text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

// 处理项目点击
const handleItemClick = (item) => {
  emit('item-click', item)
}
</script>

<style scoped>
.directory-card {
  transition: all 0.3s ease;
}

.file-item {
  transition: all 0.2s ease;
  border-radius: 8px;
  margin-bottom: 4px;
}

.file-item:hover {
  background: rgba(var(--v-theme-primary), 0.05);
  transform: translateX(4px);
}

.file-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 12px;
  cursor: pointer;
  height: 100%;
}

.file-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15) !important;
}

.file-card:active {
  transform: translateY(-2px);
}

.v-avatar {
  transition: all 0.3s ease;
}

.file-item:hover .v-avatar,
.file-card:hover .v-avatar {
  transform: scale(1.1);
}

/* 搜索框动画 */
.v-text-field {
  transition: all 0.3s ease;
}

.v-text-field:focus-within {
  transform: scale(1.02);
}

/* 视图切换按钮动画 */
.v-btn-toggle .v-btn {
  transition: all 0.2s ease;
}

.v-btn-toggle .v-btn:hover {
  transform: scale(1.05);
}

/* 列表项进入动画 */
.file-item {
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* 网格卡片进入动画 */
.file-card {
  animation: fadeInUp 0.4s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 添加延迟效果 */
.file-item:nth-child(1),
.file-card:nth-child(1) {
  animation-delay: 0.05s;
}
.file-item:nth-child(2),
.file-card:nth-child(2) {
  animation-delay: 0.1s;
}
.file-item:nth-child(3),
.file-card:nth-child(3) {
  animation-delay: 0.15s;
}
.file-item:nth-child(4),
.file-card:nth-child(4) {
  animation-delay: 0.2s;
}
.file-item:nth-child(5),
.file-card:nth-child(5) {
  animation-delay: 0.25s;
}

/* 滚动条美化 */
.v-list::-webkit-scrollbar {
  width: 6px;
}

.v-list::-webkit-scrollbar-track {
  background: transparent;
}

.v-list::-webkit-scrollbar-thumb {
  background: rgba(var(--v-theme-primary), 0.3);
  border-radius: 3px;
}

.v-list::-webkit-scrollbar-thumb:hover {
  background: rgba(var(--v-theme-primary), 0.5);
}

/* 修复滚动问题 */
.scrollable-content {
  max-height: 70vh; /* 根据需要调整高度 */
  overflow-y: auto;
}
</style>
