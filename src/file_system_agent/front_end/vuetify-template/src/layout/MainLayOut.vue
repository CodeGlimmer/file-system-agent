<template>
    <v-app :theme="theme" class="elevation-24">
        <v-app-bar title="文件系统智能体">
            <v-spacer></v-spacer>
            <v-btn
            :prepend-icon="theme === 'light' ? 'mdi-weather-sunny' : 'mdi-weather-night'"
            text="Toggle Theme"
            slim
            @click="onClick"
            ></v-btn>
        </v-app-bar>
        <v-main>
            <v-row class="fill-height">
                <v-col cols="12" md="8" class="pr-0 pa-0">
                    <!-- 消息显示区域 -->
                    <div
                        ref="messagesContainer"
                        class="messages-area pa-4 overflow-y-auto"
                    >
                        <div
                            v-for="message in messages"
                            :key="message.id"
                            class="message-wrapper mb-4"
                        >
                            <v-card
                                :class=" [
                                    'message-card',
                                    message.type === 'user' ? 'user-message ml-auto' : 'ai-message mr-auto'
                                ]"
                                :color="message.type === 'user' ? 'primary' : 'surface-variant'"
                                :variant="message.type === 'user' ? 'flat' : 'outlined'"
                                elevation="2"
                                rounded="xl"
                                max-width="80%"
                            >
                                <v-card-text class="pa-4">
                                    <!-- 打字指示器 -->
                                    <div v-if="message.isTyping" class="typing-indicator">
                                        <div class="d-flex align-center">
                                            <v-avatar color="primary" size="24" class="mr-2">
                                                <v-icon size="14" color="white">mdi-robot</v-icon>
                                            </v-avatar>
                                            <div class="typing-dots">
                                                <span></span>
                                                <span></span>
                                                <span></span>
                                            </div>
                                            <span class="ml-2 text-caption">AI正在思考...</span>
                                        </div>
                                    </div>
                                    
                                    <!-- 普通消息 -->
                                    <div v-else>
                                        <div class="d-flex align-start">
                                            <v-avatar
                                                :color="message.type === 'user' ? 'white' : 'primary'"
                                                size="32"
                                                class="mr-3"
                                            >
                                                <v-icon 
                                                    size="18" 
                                                    :color="message.type === 'user' ? 'primary' : 'white'"
                                                >
                                                    {{ message.type === 'user' ? 'mdi-account' : 'mdi-robot' }}
                                                </v-icon>
                                            </v-avatar>
                                            
                                            <div class="flex-grow-1">
                                                <!-- 消息内容 -->
                                                <div
                                                    v-if="message.markdown"
                                                    v-html="renderMarkdown(message.content)"
                                                    class="message-content markdown-content"
                                                ></div>
                                                <div
                                                    v-else
                                                    class="message-content"
                                                >
                                                    {{ message.content }}
                                                </div>
                                                
                                                <!-- 时间戳 -->
                                                <div class="text-caption opacity-70 mt-2">
                                                    {{ formatTime(message.timestamp) }}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </v-card-text>
                            </v-card>
                        </div>
                    </div>
                    
                    <!-- 固定输入区域 -->
                    <div class="input-area-fixed rounded-xl">
                        <v-divider></v-divider>
                        <div class="pa-4 rounded-xl">
                            <v-card rounded="xl" elevation="4" class="input-card">
                                <v-card-text class="pa-3">
                                    <v-textarea
                                        ref="messageInput"
                                        v-model="inputText"
                                        label="输入您的消息..."
                                        variant="plain"
                                        rows="1"
                                        auto-grow
                                        max-rows="4"
                                        hide-details
                                        @keydown.enter.exact.prevent="sendMessage"
                                        @keydown.enter.shift="() => {}"
                                        :disabled="isSending"
                                        class="message-input"
                                    ></v-textarea>
                                    
                                    <div class="d-flex align-center justify-space-between mt-2">
                                        <div class="d-flex align-center">
                                            <!-- 语音输入按钮 -->
                                            <v-btn
                                                :icon="isListening ? 'mdi-microphone-off' : 'mdi-microphone'"
                                                :color="isListening ? 'error' : 'primary'"
                                                variant="tonal"
                                                size="small"
                                                @click="toggleVoiceInput"
                                                :disabled="isSending"
                                            ></v-btn
                                            
                                            <!-- 语音状态提示 -->
                                            <v-chip
                                                v-if="isListening"
                                                color="error"
                                                size="small"
                                                class="ml-2"
                                                prepend-icon="mdi-circle"
                                            >
                                                正在录音...
                                            </v-chip>
                                        </div>
                                        
                                        <!-- 发送按钮 -->
                                        <v-btn
                                            color="primary"
                                            variant="flat"
                                            rounded="xl"
                                            :disabled="!inputText.trim() || isSending"
                                            @click="sendMessage"
                                            :loading="isSending"
                                            append-icon="mdi-send"
                                        >
                                            发送
                                        </v-btn>
                                    </div>
                                </v-card-text>
                            </v-card>
                        </div>
                    </div>
                </v-col>
                
            <!-- 浮动侧边栏 -->
            <div class="floating-sidebar" v-ripple>
                <v-card class="sidebar-card fill-height" elevation="12" rounded="lg">
                    <DirView :items="items"/>
                </v-card>
            </div>
            </v-row>
      </v-main>
    </v-app>
</template>

<script setup>
import { ref, nextTick, onMounted, watch } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import DirView from '@/views/DirView.vue'
import { getMessage } from '@/api'


const theme = ref('light')
const inputText = ref('')
const isSending = ref(false)
const isListening = ref(false)
const recognition = ref(null)
const messagesContainer = ref(null)

const messages = ref([
    {
        id: 1,
        type: 'ai',
        content: '您好！我是您的AI文件助手，有什么可以帮助您的吗？我可以回答、协助解决文件相关问题，并支持**Markdown格式**的回复！',
        timestamp: new Date(),
        markdown: true
    }
])

const items = ref([])

const onClick = () => {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
}

// 发送消息
const sendMessage = async () => {
    if (!inputText.value.trim() || isSending.value) return
    
    isSending.value = true
    
    // 添加用户消息
    const userMessage = {
        id: Date.now(),
        type: 'user',
        content: inputText.value.trim(),
        timestamp: new Date(),
        markdown: false
    }

    
    messages.value.push(userMessage)
    const messageText = inputText.value.trim()
    inputText.value = ''
    
    await nextTick()
    scrollToBottom()
    
    await AIResponse(messageText)
    
    isSending.value = false
}

const AIResponse = async (userText) => {
    // 添加打字指示器
    const typingMessage = {
        id: 'typing',
        type: 'ai',
        content: '',
        timestamp: new Date(),
        isTyping: true
    }
    
    messages.value.push(typingMessage)
    await nextTick()
    scrollToBottom()
    
    // 获取回复消息
    const { data: { reply, with_file_system, file_system} } = await getMessage(userText)
    console.log('AI回复:', reply)
    // 移除打字指示器
    messages.value = messages.value.filter(msg => msg.id !== 'typing')
    
    // 生成AI回复
    const aiMessage = {
        id: Date.now(),
        type: 'ai',
        content: reply,
        timestamp: new Date(),
        markdown: true
    }
    if (with_file_system && file_system) {
        items.value = file_system
    }
    
    messages.value.push(aiMessage)
    await nextTick()
    scrollToBottom()
}

// 初始化语音识别
const initVoiceRecognition = () => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
        recognition.value = new SpeechRecognition()
        
        recognition.value.continuous = false
        recognition.value.interimResults = false
        recognition.value.lang = 'zh-CN'
        
        recognition.value.onstart = () => {
            isListening.value = true
        }
        
        recognition.value.onresult = (event) => {
            const transcript = event.results[0][0].transcript
            inputText.value += transcript
            isListening.value = false
        }
        
        recognition.value.onerror = (event) => {
            console.error('语音识别错误:', event.error)
            isListening.value = false
        }
        
        recognition.value.onend = () => {
            isListening.value = false
        }
    }
}

// 切换语音输入
const toggleVoiceInput = () => {
    if (!recognition.value) {
        alert('您的浏览器不支持语音识别功能')
        return
    }
    
    if (isListening.value) {
        recognition.value.stop()
    } else {
        recognition.value.start()
    }
}

// 渲染Markdown
const renderMarkdown = (content) => {
    try {
        const html = marked.parse(content)
        return DOMPurify.sanitize(html)
    } catch (error) {
        console.error('Markdown解析错误:', error)
        return content
    }
}

// 格式化时间
const formatTime = (timestamp) => {
    return new Intl.DateTimeFormat('zh-CN', {
        hour: '2-digit',
        minute: '2-digit'
    }).format(timestamp)
}

// 滚动到底部
const scrollToBottom = () => {
    if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
}

// 监听消息变化并自动滚动
watch(messages, () => {
    nextTick(() => {
        scrollToBottom()
    })
}, { deep: true })

onMounted(() => {
    initVoiceRecognition()
    scrollToBottom()
})
</script>

<style scoped>
.messages-area {
    height: calc(100vh - 64px - 140px); /* 视口高度 - app-bar - 输入区域高度 */
    overflow-y: auto;
    background: rgba(var(--v-theme-surface), 0.3);
    scroll-behavior: smooth;
}

.messages-area::-webkit-scrollbar {
    width: 6px;
}

.messages-area::-webkit-scrollbar-track {
    background: transparent;
}

.messages-area::-webkit-scrollbar-thumb {
    background: rgba(var(--v-theme-primary), 0.3);
    border-radius: 3px;
}

/* 固定输入区域 */
.input-area-fixed {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 66.666667%; /* 8/12 的列宽 */
    background: rgb(var(--v-theme-surface));
    z-index: 100;
    box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.08);
}

/* 响应式：在小屏幕上占满宽度 */
@media (max-width: 960px) {
    .input-area-fixed {
        width: 100%;
    }
    
    .messages-area {
        height: calc(100vh - 64px - 140px);
    }
}

/* 中等屏幕适配 */
@media (min-width: 960px) and (max-width: 1264px) {
    .input-area-fixed {
        width: 60%;
    }
}

/* 大屏幕适配 */
@media (min-width: 1904px) {
    .input-area-fixed {
        width: 70%;
    }
}

.message-card {
    transition: all 0.2s ease;
    animation: fadeInUp 0.3s ease-out;
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.message-card:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
}

.user-message {
    background: linear-gradient(135deg, rgb(var(--v-theme-primary)), rgba(var(--v-theme-primary), 0.8));
    color: white;
}

.typing-indicator .typing-dots {
    display: flex;
    gap: 4px;
}

.typing-dots span {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: rgb(var(--v-theme-primary));
    animation: typing 1.4s infinite ease-in-out;
}

.typing-dots span:nth-child(1) { animation-delay: -0.32s; }
.typing-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing {
    0%, 80%, 100% {
        transform: scale(0.8);
        opacity: 0.5;
    }
    40% {
        transform: scale(1);
        opacity: 1;
    }
}

.input-card {
    border: 2px solid transparent;
    transition: border-color 0.2s ease;
    background: rgb(var(--v-theme-surface));
}

.input-card:focus-within {
    border-color: rgb(var(--v-theme-primary));
}

.message-content {
    word-break: break-word;
    line-height: 1.6;
}

/* Markdown 样式 */
.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3) {
    margin: 16px 0 8px 0;
    font-weight: 600;
    color: rgb(var(--v-theme-primary));
}

.markdown-content :deep(p) {
    margin: 8px 0;
}

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
    margin: 8px 0;
    padding-left: 20px;
}

.markdown-content :deep(li) {
    margin: 4px 0;
}

.markdown-content :deep(code) {
    background: rgba(var(--v-theme-primary), 0.1);
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'Monaco', 'Consolas', monospace;
    font-size: 0.9em;
}

.markdown-content :deep(pre) {
    background: rgba(0, 0, 0, 0.05);
    padding: 16px;
    border-radius: 8px;
    overflow-x: auto;
    margin: 12px 0;
    border-left: 4px solid rgb(var(--v-theme-primary));
}

.markdown-content :deep(pre code) {
    background: none;
    padding: 0;
}

.markdown-content :deep(blockquote) {
    border-left: 4px solid rgb(var(--v-theme-primary));
    margin: 12px 0;
    padding: 12px 16px;
    background: rgba(var(--v-theme-primary), 0.05);
    border-radius: 0 8px 8px 0;
}

.markdown-content :deep(table) {
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0;
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid rgba(var(--v-theme-primary), 0.2);
}

.markdown-content :deep(th),
.markdown-content :deep(td) {
    padding: 12px 16px;
    text-align: left;
    border-bottom: 1px solid rgba(var(--v-theme-primary), 0.1);
}

.markdown-content :deep(th) {
    background: rgba(var(--v-theme-primary), 0.1);
    font-weight: 600;
    color: rgb(var(--v-theme-primary));
}

/* 浮动侧边栏样式 */
.floating-sidebar {
    position: fixed;
    top: 64px; /* v-app-bar 的高度 */
    right: 0;
    width: 33.333333%; /* 4/12 的列宽 */
    height: calc(100vh - 64px);
    z-index: 10;
    padding: 16px;
    pointer-events: none;
}

.sidebar-card {
    pointer-events: auto;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12) !important;
}

/* 响应式：在小屏幕上隐藏或调整 */
@media (max-width: 960px) {
    .floating-sidebar {
        display: none;
    }
}

/* 中等屏幕适配 */
@media (min-width: 960px) and (max-width: 1264px) {
    .floating-sidebar {
        width: 40%;
    }
}

/* 大屏幕适配 */
@media (min-width: 1904px) {
    .floating-sidebar {
        width: 30%;
    }
}
</style>