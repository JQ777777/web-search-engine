import { createStore } from 'vuex';
import createPersistedState from 'vuex-persistedstate';
import axios from 'axios';

// 计算内容权重的辅助函数
function calculateContentWeight(content, user) {
  if (!user || !user.username) return 0;

  const { searchHistory, clickedDocuments } = user;
  const { title, id } = content; // 假设 content 对象有 title 和 id 属性

  // 搜索历史中的词权重较大
  const searchWeight = searchHistory.includes(title) ? 1 : 0;

  // 点击过的文档权重较小
  const clickWeight = clickedDocuments[id] ? -clickedDocuments[id] : 0;

  // 综合权重
  return searchWeight + clickWeight;
}

export default createStore({
  state: {
    isAuthenticated: false,
    currentUser: null, // 存储当前用户信息
    users: {} // 存储所有用户的搜索历史和点击行为
  },
  mutations: {
    setAuthenticated(state, status) {
      state.isAuthenticated = status;
    },
    setCurrentUser(state, user) {
      if (user) {
        // 如果用户存在，则初始化或加载用户的搜索历史
        if (!state.users[user.username]) {
          state.users[user.username] = { searchHistory: [], clickedDocuments: {} };
        }
        state.currentUser = user;
      } else {
        state.currentUser = null;
      }
    },
    setSearchHistory(state, { username, history }) {
      if (state.users[username]) {
        state.users[username].searchHistory = history;
      }
    },
    addSearchHistory(state, query) {
      if (state.isAuthenticated && state.currentUser) {
        const username = state.currentUser.username;
        if (!state.users[username]) {
          state.users[username] = { searchHistory: [], clickedDocuments: {} };
        }
        state.users[username].searchHistory.push(query);
      }
    },
    addClickedDocument(state, { username, docId }) {
      // 检查参数是否有效
      if (!username || !docId) {
        console.error('Invalid parameters: username or docId is undefined');
        return;
      }
    
      // 检查用户是否已登录
      if (!state.isAuthenticated || !state.currentUser) {
        console.error('User is not authenticated');
        return;
      }
    
      // 检查用户名是否匹配当前用户
      if (username !== state.currentUser.username) {
        console.error('Username does not match current user');
        return;
      }
    
      // 初始化用户数据
      if (!state.users[username]) {
        state.users[username] = { searchHistory: [], clickedDocuments: {} };
      }
    
      // 更新点击文档记录
      state.users[username].clickedDocuments[docId] = (state.users[username].clickedDocuments[docId] || 0) + 1;
    },
    recordClick(state, { username, docId }) {
      if (!state.users[username]) {
        state.users[username] = {
          searchHistory: [],
          clickedDocuments: {}
        };
      }

      if (!state.users[username].clickedDocuments[docId]) {
        state.users[username].clickedDocuments[docId] = 1;
      } else {
        state.users[username].clickedDocuments[docId]++;
      }
    },
    setUser(state, user) {
      state.user = user;
    },
    setLoading(state, status) {
      state.loading = status;
    },
    setError(state, error) {
      state.error = error;
    }
  },
  actions: {
    login({ commit }, user) {
      commit('setAuthenticated', true);
      commit('setCurrentUser', user);
    },
    logout({ commit }) {
      commit('setAuthenticated', false);
      commit('setCurrentUser', null);
    },
    // 新增 action：根据用户的行为对内容进行排序
    sortContentByUserBehavior({ getters }, contents) {
      const currentUser = getters.currentUser;
      if (!currentUser) return contents;

      // 根据用户的搜索历史和点击行为计算每个内容的权重
      return contents.sort((a, b) => {
        const weightA = calculateContentWeight(a, currentUser);
        const weightB = calculateContentWeight(b, currentUser);

        // 权重较高的内容排在前面
        return weightB - weightA;
      });
    },
    async fetchUser({ commit }, userId) {
      try {
        commit('setLoading', true);
        const response = await axios.get(`http://your-api-endpoint/user/${userId}`);
        commit('setUser', response.data);
        commit('setLoading', false);
      } catch (error) {
        commit('setError', error.message || 'Failed to fetch user data');
        commit('setLoading', false);
      }
    }
  },
  getters: {
    getUser: (state) => state.user,
    isLoading: (state) => state.loading,
    getError: (state) => state.error,
    isAuthenticated: (state) => state.isAuthenticated,
    currentUser: (state) => state.currentUser,
    user: (state) => (username) => state.users[username] || null,
    searchHistory: (state, getters) => {
      const currentUser = getters.currentUser;
      return currentUser ? state.users[currentUser.username]?.searchHistory || [] : [];
    },
    clickedDocuments: (state, getters) => {
      const currentUser = getters.currentUser;
      return currentUser ? state.users[currentUser.username]?.clickedDocuments || {} : {};
    }
  },
  plugins: [
    createPersistedState({
      key: 'my-app',
      paths: ['isAuthenticated', 'currentUser', 'users']
    })
  ]
});