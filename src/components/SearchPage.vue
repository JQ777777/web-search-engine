<template>
  <div class="search-container">
    <!-- 添加标题 -->
    <h1 class="title">欢迎进入我的搜索引擎</h1>

    <!-- 用户状态显示 -->
    <div class="auth-container">
      <div v-if="!isAuthenticated" class="auth-buttons">
        <button @click="goToAuth(true)" class="auth-button auth-login">登录</button>
        <button @click="goToAuth(false)" class="auth-button auth-register">注册</button>
      </div>
      <div v-else class="user-info">
        <p>欢迎, {{ currentUser.username }}!</p>
        <button @click="logout" class="auth-button auth-logout">退出登录</button>
      </div>
    </div>

    <!-- 查询类型选择和搜索框 -->
    <div class="search-form">
      <!-- 查询类型选择 -->
      <div class="query-type-buttons">
        <label v-for="(type, index) in searchTypes" :key="index">
          <input type="radio" v-model="searchType" :value="type.value">{{ type.label }}
        </label>
      </div>

      <!-- 搜索框 -->
      <input
        v-model="query"
        placeholder="请输入搜索内容"
        class="search-input"
        @input="fetchSuggestions"
      />

      <!-- 搜索建议 -->
      <ul v-if="suggestions.length" class="suggestions-list">
        <li v-for="(suggestion, index) in suggestions" :key="index" @click="selectSuggestion(suggestion)">
          {{ suggestion }}
        </li>
      </ul>

      <!-- 查询历史 -->
      <div v-if="searchHistory.length" class="search-history">
        <ul>
          <li v-for="(item, index) in searchHistory" :key="index" @click="setQuery(item)">
            {{ item }}
          </li>
        </ul>
        <button @click="clearHistory" class="clear-history-button">清除历史</button>
      </div>

      <!-- 搜索按钮 -->
      <button @click="performSearch" class="search-button">搜索</button>
    </div>

    <!-- 推荐内容，显示在搜索结果上方 -->
<div v-if="showRecommendations">
  <h2>为您推荐</h2>
  <ul v-if="recommendations.length">
    <li v-for="(recommendation, index) in recommendations" :key="index">
      <!-- 使用 a 标签进行外部跳转 -->
      <a :href="recommendation.link" target="_blank" rel="noopener noreferrer" @click="trackClick(recommendation)">
        {{ recommendation.title }}
      </a>
    </li>
  </ul>
  <p v-else>没有找到相关的推荐。</p>
</div>

    <!-- 搜索结果展示 -->
    <div v-if="results && results.hits.hits.length" class="results-list">
      <ResultItem
        v-for="item in results.hits.hits"
        :key="item._id"
        :item="item"
        :query="query"
      />
    </div>

    <!-- 无结果提示 -->
    <div v-else-if="!loading && (!results || !results.hits || !results.hits.hits.length)" class="no-results">
      <p>没有找到相关结果。</p>
    </div>

    <!-- 加载中提示 -->
    <div v-if="loading" class="loading">
      <p>正在加载...</p>
    </div>

  </div>
</template>

<script>
import { search } from '../services/esservice';
import ResultItem from "../components/ResultItem.vue";
import {getRecommendations } from '../services/esservice';

export default {
  components: {
    ResultItem
  },
  data() {
    return {
      query: '',
      searchType: 'multi_match', // 默认选择普通查询
      searchTypes: [
        { label: '普通查询', value: 'multi_match' },
        { label: '短语查询', value: 'match_phrase' },
        { label: '通配查询', value: 'wildcard' }
      ],
      results: null,
      loading: false,
      indexName: this.$route.params.index || 'nku_index', // 默认索引为 'nku_index'
      suggestions: [], // 新增：用于存储搜索建议
      popularSearches: ["Vue.js", "JavaScript", "Elasticsearch", "Node.js", "React"], // 预定义的热门搜索词
      recommendations: [], // 用于存储推荐新闻
      showRecommendations: false,
    };
  },
  computed: {
    isAuthenticated() {
      return this.$store.state.isAuthenticated;
    },
    currentUser() {
      return this.$store.state.currentUser;
    },
    searchHistory() {
      if (this.isAuthenticated && this.currentUser) {
        return this.$store.state.users[this.currentUser.username].searchHistory || [];
      }
      return [];
    }
  },
  watch: {
    '$route.params.query'(newQuery) {
      if (newQuery) {
        this.query = newQuery;
        this.performSearch();
      }
    },
    '$route.params.index'(newIndex) {
      this.indexName = newIndex || 'nku_index';
      if (this.query) {
        this.performSearch();
      }
    },
    relatedNews(newVal) {
      console.log('relatedNews updated:', newVal);
    },
    results(newVal) {
      console.log('results updated:', newVal);
    }
  },
  mounted() {
    const { query, newsId } = this.$route.params;
    if (query) {
      console.log('Performing search with query:', query);
      this.query = query;
      this.performSearch();
    }
    if (newsId) {
      console.log('Fetching related news for news ID:', newsId);
      this.fetchRelatedNews(newsId);
    }
    // 获取个性化推荐
    this.fetchRecommendations();
  },
  methods: {
    goToAuth(isLogin) {
      console.log('Go to Auth:', isLogin);
      this.$router.push({
        name: 'Auth',
        query: { mode: isLogin ? 'login' : 'register' } // 通过查询参数传递模式
      });
      console.log('After router push');
    },
    logout() {
      console.log('Logout');
      this.$store.dispatch('logout');
      this.$router.push('/'); // 退出登录后跳转到首页
    },
    async performSearch() {
      // 检查查询是否有效
      if (!this.query || typeof this.query !== 'string') {
        console.warn('Invalid query:', this.query);
        return;
      }

      this.loading = true;
      try {
        console.log('Performing search with query:', this.query.trim());

        // 构建查询对象
        const queryBody = this.buildQueryBody();

        // 执行查询
        this.results = await search(queryBody, this.indexName);
        console.log('Search results:', this.results);

        if (!this.results || !this.results.hits || !this.results.hits.hits.length) {
          console.warn('No results found for query:', this.query);
        } else {
          // 如果有结果，显示推荐内容
          this.showRecommendations = true;

          // 获取推荐内容
          await this.fetchRecommendations();
        }

        // 存储查询记录（仅当用户已登录时）
        if (this.isAuthenticated && this.currentUser) {
          this.$store.commit('addSearchHistory', this.query.trim());
        }
      } catch (error) {
        console.error('Failed to perform search:', error);
      } finally {
        this.loading = false;
      }
    },
    async fetchRecommendations() {
      try {
        if (!this.isAuthenticated || !this.currentUser) {
          // 如果用户未登录，则可以提供一些默认或热门的推荐
          this.recommendations = await getRecommendations('default');
          return;
        }

        const userSearchHistory = this.searchHistory;
        const userClickedDocuments = this.$store.state.users[this.currentUser.username]?.clickedDocuments || {};

        // 使用用户的查询历史和点击记录作为参数来获取推荐
        const rawRecommendations = await getRecommendations({
          history: userSearchHistory,
          clicked: userClickedDocuments,
          count: 5 // 只需要5条推荐
        });

        // 确保每个推荐对象都有 url 属性
      this.recommendations = rawRecommendations.map(recommendation => ({
        ...recommendation,
        id: recommendation.id
      }));

        console.log('Fetched recommendations:', this.recommendations);
      } catch (error) {
        console.error('Failed to fetch recommendations:', error);
      }
    },
    trackClick(recommendation) {
  console.log('Clicked on recommendation:', recommendation);

  // 如果用户已登录，记录点击行为
  if (this.isAuthenticated && this.currentUser) {
    this.$store.commit('addClickedDocument', {
      username: this.currentUser.username,
      documentId: recommendation.id || recommendation.link
    });
  } else {
    console.error('User is not authenticated');
    return;
  }

  // 跳转到文章对应的 URL
  if (recommendation.id) {
    window.location.href = recommendation.id;
  } else {
    console.error('Invalid recommendation object:', recommendation);
  }
},
  
  
    getSortedContents() {
      const contents = this.allContents; // 从某个地方获取内容列表
      return this.$store.dispatch('sortContentByUserBehavior', contents);
    },
   
    buildQueryBody() {
      const query = this.query.trim();
      const userSearchHistory = this.searchHistory;
      const userClickedDocuments = this.$store.state.users[this.currentUser.username]?.clickedDocuments || {};

      if (this.searchType === 'multi_match') {
        return {
          size: 10,
          query: {
            function_score: {
              query: {
                multi_match: {
                  query: query,
                  fields: ["title", "keywords", "description", "content"],
                  analyzer: "ik_max_word",
                  type: "best_fields",
                  operator: "OR"
                }
              },
              functions: [
                ...userSearchHistory.map(term => ({
                  filter: { match: { content: term } },
                  weight: 1.5 // 可以根据需要调整权重
                })),
                ...Object.keys(userClickedDocuments).map(docId => ({
                  filter: { term: { _id: docId } },
                  weight: -userClickedDocuments[docId] * 0.5 // 点击次数越多，权重越低
                }))
              ],
              score_mode: "sum", // 使用 sum 模式将所有评分相加
              boost_mode: "multiply" // 将函数评分与原始评分相乘
            }
          },
          highlight: {
            fields: {
              title: {},
              keywords: {},
              description: {},
              content: {}
            }
          },
          _source: ["title", "keywords", "description", "content", "html_filename","links"],
          sort: [
            { "_score": { "order": "desc" } },
            { "pr": { "order": "desc" }}
          ]
        };
      } else if (this.searchType === 'match_phrase') {
        return {
          size: 10,
          query: {
            function_score: {
              query: {
                match_phrase: {
                  content: query
                }
              },
              functions: [
                ...userSearchHistory.map(term => ({
                  filter: { match_phrase: { content: term } },
                  weight: 1.5
                })),
                ...Object.keys(userClickedDocuments).map(docId => ({
                  filter: { term: { _id: docId } },
                  weight: -userClickedDocuments[docId] * 0.5 // 点击次数越多，权重越低
                }))
              ],
              score_mode: "sum",
              boost_mode: "multiply" // 将函数评分与原始评分相乘
            }
          },
          highlight: {
            fields: {
              content: {}
            }
          },
          _source: ["title", "keywords", "description", "content", "html_filename","links"],
          sort: [
            { "_score": { "order": "desc" } },
            { "pr": { "order": "desc" }}
          ]
        };
      } else if (this.searchType === 'wildcard') {
        return {
          size: 10,
          query: {
            function_score: {
              query: {
                wildcard: {
                  content: query
                }
              },
              functions: [
                ...userSearchHistory.map(term => ({
                  filter: { wildcard: { content: term } },
                  weight: 1.5
                })),
                ...Object.keys(userClickedDocuments).map(docId => ({
                  filter: { term: { _id: docId } },
                  weight: -userClickedDocuments[docId] * 0.5 // 点击次数越多，权重越低
                }))
              ],
              score_mode: "sum",
              boost_mode: "multiply" // 将函数评分与原始评分相乘
            }
          },
          highlight: {
            fields: {
              content: {}
            }
          },
          _source: ["title", "keywords", "description", "content", "html_filename","links"],
          sort: [
            { "_score": { "order": "desc" } },
            { "pr": { "order": "desc" }}
          ]
        };
      } else {
        throw new Error('Unknown search type');
      }
    },

    setQuery(query) {
      this.query = query;
      this.performSearch();
    },
    clearHistory() {
      if (this.isAuthenticated && this.currentUser) {
        this.$store.commit('setSearchHistory', {
          username: this.currentUser.username,
          history: []
        });
      }
    },
    fetchSuggestions() {
      if (this.query.trim() === '') {
        this.suggestions = [];
        return;
      }

      // Combine the user's search history and popular searches, then filter by the current query
      const combined = [...this.searchHistory, ...this.popularSearches];
      this.suggestions = combined.filter(suggestion =>
        suggestion.toLowerCase().includes(this.query.toLowerCase())
      ).slice(0, 5); // Limit to 5 suggestions
    },
    selectSuggestion(suggestion) {
      this.query = suggestion;
      this.suggestions = [];
      this.performSearch();
    }
  }
};
</script>

<style scoped>
/* 全局样式 */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

/* 容器样式 */
.search-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 20px;
  background-color: #f5f5f5;
}

/* 标题样式 */
.title {
  font-size: 2rem;
  margin-bottom: 20px;
  color: #333;
  text-align: center;
}

/* 搜索表单样式 */
.search-form {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  max-width: 600px;
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* 查询类型按钮样式 */
.query-type-buttons {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.query-type-buttons label {
  font-size: 1rem;
  color: #555;
  cursor: pointer;
}

.query-type-buttons input[type="radio"] {
  margin-right: 5px;
}

/* 搜索框样式 */
.search-input {
  width: 100%;
  padding: 10px;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  margin-bottom: 10px;
  transition: border-color 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #007bff;
}

/* 查询历史样式 */
.search-history ul {
  list-style: none;
  padding: 0;
  margin-bottom: 10px;
}

.search-history li {
  padding: 5px 10px;
  border-bottom: 1px solid #ddd;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.search-history li:hover {
  background-color: #f0f0f0;
}

.clear-history-button {
  width: 100%;
  padding: 10px;
  font-size: 1rem;
  color: #fff;
  background-color: #dc3545;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  margin-bottom: 20px; /* 增加底部外边距 */
}

.clear-history-button:hover {
  background-color: #c82333;
}

/* 搜索按钮样式 */
.search-button {
  width: 100%;
  padding: 10px;
  font-size: 1rem;
  color: #fff;
  background-color: #007bff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.search-button:hover {
  background-color: #0056b3;
}

/* 结果列表样式 */
.results-list {
  width: 100%;
  max-width: 600px;
  margin: 20px auto;
}

.results-list ul {
  list-style: none;
  padding: 0;
}

.results-list li {
  padding: 10px;
  border-bottom: 1px solid #ddd;
}

/* 无结果提示样式 */
.no-results {
  margin-top: 20px;
  font-size: 1.2rem;
  color: #777;
  text-align: center;
}

/* 加载中提示样式 */
.loading {
  margin-top: 20px;
  font-size: 1.2rem;
  color: #777;
  text-align: center;
}

/* 用户状态容器样式 */
.auth-container {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px; /* 调整与下方内容的距离 */
}

/* 按钮容器样式 */
.auth-buttons,
.user-info {
  display: flex;
  align-items: center;
  gap: 10px; /* 按钮之间的间距 */
}

/* 用户信息样式 */
.user-info p {
  font-size: 1.2rem;
  color: #333;
  margin-right: 10px; /* 与退出按钮的距离 */
}

/* 按钮基础样式 */
.auth-button {
  padding: 10px 20px;
  font-size: 1rem;
  color: #fff;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.2s ease;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

/* 登录按钮样式 */
.auth-login {
  background-color: #007bff; /* 蓝色 */
}

.auth-login:hover {
  background-color: #0056b3; /* 深蓝色 */
  transform: scale(1.05); /* 悬停时放大 */
}

/* 注册按钮样式 */
.auth-register {
  background-color: #28a745; /* 绿色 */
}

.auth-register:hover {
  background-color: #218838; /* 深绿色 */
  transform: scale(1.05); /* 悬停时放大 */
}

/* 退出登录按钮样式 */
.auth-logout {
  background-color: #dc3545; /* 红色 */
}

.auth-logout:hover {
  background-color: #c82333; /* 深红色 */
  transform: scale(1.05); /* 悬停时放大 */
}

.related-news {
  margin-top: 20px;
}

.related-news h3 {
  font-size: 18px;
  margin-bottom: 10px;
}

.related-news ul {
  list-style-type: none;
  padding: 0;
}

.related-news li {
  margin-bottom: 5px;
}

.related-news a:hover {
  text-decoration: underline;
}
</style>