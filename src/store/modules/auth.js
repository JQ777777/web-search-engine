// src/store/modules/auth.js
const state = {
    authenticated: false,
    currentUser: null,
    searchHistory: {} // 用户搜索历史，以用户 ID 为键
  };
  
  const mutations = {
    SET_AUTHENTICATED(state, value) {
      state.authenticated = value;
    },
    SET_CURRENT_USER(state, user) {
      state.currentUser = user;
      if (!state.searchHistory[user.id]) {
        state.searchHistory[user.id] = [];
      }
    },
    ADD_SEARCH_HISTORY(state, { userId, query }) {
      if (state.searchHistory[userId]) {
        const history = [...new Set([query, ...state.searchHistory[userId]])]; // 去重
        state.searchHistory[userId] = history.slice(0, 10); // 限制最多10条历史记录
      }
    },
    CLEAR_SEARCH_HISTORY(state, userId) {
      if (state.searchHistory[userId]) {
        state.searchHistory[userId] = [];
      }
    }
  };
  
  const actions = {
    login({ commit }, user) {
      return new Promise((resolve) => {
        setTimeout(() => {
          commit('SET_AUTHENTICATED', true);
          commit('SET_CURRENT_USER', user);
          resolve();
        }, 1000);
      });
    },
    logout({ commit }) {
      commit('SET_AUTHENTICATED', false);
      commit('SET_CURRENT_USER', null);
      commit('CLEAR_SEARCH_HISTORY', null); // 清除当前用户的搜索历史
    }
  };
  
  const getters = {
    isAuthenticated: state => state.authenticated,
    currentUser: state => state.currentUser,
    getUserSearchHistory: state => userId => state.searchHistory[userId] || []
  };
  
  export default {
    namespaced: true,
    state,
    mutations,
    actions,
    getters
  };