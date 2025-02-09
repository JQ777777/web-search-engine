<template>
  <div class="result-item" @click="toggleDetails">
    <div class="result-header">
      <h2 class="result-title">{{ item._source.title }}</h2>
      <p class="result-keywords">{{ truncatedKeywords }}</p>
    </div>
    <p class="result-description">{{ truncatedDescription }}</p>
    <p class="result-content" v-html="highlightedAndTruncatedContent"></p>
    <button v-if="!showDetails" class="view-details">查看详情</button>
    <div v-else class="details">
      <!-- 只显示标题、关键词、描述和内容 -->
      <div class="details-section">
        <h3>标题</h3>
        <p>{{ item._source.title }}</p>
      </div>
      <div class="details-section">
        <h3>关键词</h3>
        <p>{{ item._source.keywords }}</p>
      </div>
      <div class="details-section">
        <h3>描述</h3>
        <p>{{ item._source.description }}</p>
      </div>
      <div class="details-section">
        <h3>内容</h3>
        <p v-html="item._source.content"></p>
      </div>

      <!-- 相关文件部分 -->
      <div v-if="relatedFiles.length > 0" class="details-section">
        <h3>相关文件</h3>
        <ul>
          <li v-for="(file, index) in relatedFiles" :key="index">
            <a :href="file.link" target="_blank">{{ file.name }}</a>
          </li>
        </ul>
      </div>

      <button @click.stop="loadHtmlSnapshot" class="snapshot-button">网页快照</button>
      <button @click.stop="toggleDetails" class="close-details">关闭详情</button>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    result: Object,
    item: {
      type: Object,
      required: true,
      validator: (value) => {
        return value && typeof value === 'object' && value._source && typeof value._source === 'object';
      }
    },
    query: String
  },
  data() {
    return {
      showDetails: false,
      relatedFiles: []
    };
  },
  computed: {
    truncatedKeywords() {
      return this.truncate(this.item._source.keywords, 50);
    },
    truncatedDescription() {
      return this.truncate(this.item._source.description, 100);
    },
    highlightedAndTruncatedContent() {
      return this.highlightQuery(this.item._source.content, this.query, 400);
    }
  },
  methods: {
    handleClick() {
      // 记录用户点击的文档ID
      if (this.isAuthenticated && this.currentUser) {
        this.$store.commit('addClickedDocument', {
          username: this.currentUser.username,
          docId: this.result._id
        });
      }

      // 跳转到文档详情页或其他操作
      this.$router.push(`/news/${this.result._id}`);
    },
    toggleDetails() {
      this.showDetails = !this.showDetails;
      this.showSnapshot = false; // 点击“关闭详情”时隐藏 iframe
    },
    truncate(value, length) {
      if (!value) return '';
      return value.length > length ? value.substring(0, length) + '...' : value;
    },
    highlightQuery(value, query, maxLength) {
      if (!query || !value) return this.truncate(value, maxLength);
      const regex = new RegExp(`(${query})`, 'gi');
      const highlighted = value.replace(regex, '<span class="highlight">$1</span>');
      return this.truncate(highlighted, maxLength);
    },
    loadHtmlSnapshot() {
    const htmlFilename = this.item._source.html_filename;
    console.log('HTML Filename:', htmlFilename);  // 调试输出
    if (htmlFilename) {
      const fullPath = `/html_files/${htmlFilename}`;
      console.log('Full Path:', fullPath);  // 调试输出
      const absolutePath = `${window.location.origin}${fullPath}`;
      console.log('Absolute Path:', absolutePath);  // 调试输出
      this.$router.push({ name: 'HtmlSnapshot', params: { id: absolutePath } });
    } else {
      alert('此结果没有网页快照。');
    }
  },
    getRelatedFiles() {
  console.log('Links in item:', this.item._source.links); // 调试输出
  const links = this.item._source.links || [];

  this.relatedFiles = links.map(link => {
    try {
      const url = new URL(link.link);
      const path = url.pathname;
      const name = path.substring(path.lastIndexOf('/') + 1); // 提取文件名
      const match = name.match(/\.([^.]+)$/);
      const ext = match ? match[1].toLowerCase() : '';

      console.log('File extension:', ext); // 调试输出
      // 只保留符合条件的文件类型
      if (['doc', 'docx', 'pdf'].includes(ext)) {
        return {
          name,
          link: link.link
        };
      }
    } catch (error) {
      console.error('Invalid URL:', link.link, error);
    }

    return null;
  }).filter(Boolean); // 过滤掉不符合条件的项

  console.log('Filtered Related Files:', this.relatedFiles); // 输出筛选后的相关文件
}
  },
  mounted() {
    console.log('Item:', this.item); // 打印整个 item 对象
    this.getRelatedFiles();
  },
  watch: {
  item: {
    handler(newVal) {
      if (newVal) {
        this.getRelatedFiles();
      }
    },
    immediate: true
  }
}
};
</script>

<style scoped>
.result-item {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
  cursor: pointer;
  transition: box-shadow 0.3s ease;
}

.result-item:hover {
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.result-title {
  font-size: 1.4rem;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.result-keywords {
  font-size: 0.9rem;
  color: red;
  margin: 0;
  opacity: 0.8;
}

.result-description {
  font-size: 1rem;
  color: #777;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: normal; /* 允许换行 */
  display: -webkit-box; /* 使用弹性盒子布局 */
  -webkit-line-clamp: 2; /* 限制为2行 */
  -webkit-box-orient: vertical; /* 垂直布局 */
  margin-top: 5px;
}

.result-content {
  font-size: 1rem;
  color: #555;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: normal; /* 允许换行 */
  display: -webkit-box; /* 使用弹性盒子布局 */
  -webkit-line-clamp: 5; /* 限制为5行 */
  -webkit-box-orient: vertical; /* 垂直布局 */
  margin-top: 10px;
}

.view-details {
  margin-top: 15px;
  padding: 8px 16px;
  font-size: 1rem;
  color: #fff;
  background-color: #007bff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.view-details:hover {
  background-color: #0056b3;
}

.details {
  margin-top: 20px;
  padding: 20px;
  background-color: #f9f9f9;
  border: 1px solid #ccc;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
}

.details-section {
  margin-bottom: 20px;
}

.details-section h3 {
  font-size: 1.2rem;
  font-weight: bold;
  color: #333;
  margin: 0 0 5px 0;
}

.details-section p {
  font-size: 1rem;
  color: #555;
  margin: 0;
}

.close-details {
  margin-top: 20px;
  padding: 8px 16px;
  font-size: 1rem;
  color: #fff;
  background-color: #ff4d4d;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.close-details:hover {
  background-color: #e03e3e;
}

.snapshot-button {
  margin-top: 15px;
  padding: 8px 16px;
  font-size: 1rem;
  color: #fff;
  background-color: #28a745; /* 绿色 */
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.snapshot-button:hover {
  background-color: #218838;
}

.highlight {
  background-color: #ffeb3b;
}
</style>