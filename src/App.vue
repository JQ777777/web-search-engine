<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script>
export default {
  created() {
    this.$store.dispatch('fetchUser'); // 在应用启动时检查用户状态
  },
  data() {
    return {
      user: null,
      loading: false,
      error: null
    };
  },
  methods: {
    async loadUser() {
      try {
        await this.$store.dispatch('fetchUser', { userId: 123 }); // 确保传递正确的 userId
        this.user = this.$store.getters.getUser;
        this.loading = this.$store.getters.isLoading;
        this.error = this.$store.getters.getError;
      } catch (error) {
        console.error('Failed to load user data:', error);
      }
    }
  }
};
</script>

<style lang="less">
  #app {
    font-family: 'Avenir', Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    /*text-align: center;*/
    color: #2c3e50;
  }

  #nav {
    padding: 30px;

    a {
      font-weight: bold;
      color: #2c3e50;

      &.router-link-exact-active {
        color: #42b983;
      }
    }
  }
</style>