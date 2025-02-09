<template>
  <div class="auth-container">
    <h1>{{ mode === 'login' ? '登录' : '注册' }}</h1>

    <!-- 登录表单 -->
    <form v-if="mode === 'login'" @submit.prevent="handleLogin">
      <div class="form-group">
        <label for="username">用户名</label>
        <input type="text" id="username" v-model="username" required />
      </div>
      <div class="form-group">
        <label for="password">密码</label>
        <input type="password" id="password" v-model="password" required />
      </div>
      <button type="submit">登录</button>
      <p>还没有账号？ <a @click="toggleMode">立即注册</a></p>
    </form>

    <!-- 注册表单 -->
    <form v-else @submit.prevent="handleRegister">
      <div class="form-group">
        <label for="username">用户名</label>
        <input type="text" id="username" v-model="username" required />
      </div>
      <div class="form-group">
        <label for="email">邮箱</label>
        <input type="email" id="email" v-model="email" required />
      </div>
      <div class="form-group">
        <label for="password">密码</label>
        <input type="password" id="password" v-model="password" required />
      </div>
      <button type="submit">注册</button>
      <p>已有账号？ <a @click="toggleMode">立即登录</a></p>
    </form>
  </div>
</template>

<script>
export default {
  data() {
    return {
      username: '',
      password: '',
      email: '', // 仅用于注册表单
      mode: 'login' // 默认为登录模式
    };
  },
  created() {
    // 初始化时根据 URL 查询参数设置 mode
    this.updateModeFromRoute();
  },
  watch: {
    // 监听路由变化，自动更新 mode
    '$route.query.mode'() {
    this.updateModeFromRoute();
  }
  },
  methods: {
    // 根据路由查询参数更新 mode
    updateModeFromRoute() {
      const mode = this.$route.query.mode || 'login';
      if (mode !== this.mode) {
        this.mode = mode;
        console.log('Mode updated to:', this.mode);
      }
    },
    toggleMode() {
      // 切换登录/注册模式
      const newMode = this.mode === 'login' ? 'register' : 'login';
      this.$router.push({ name: 'Auth', query: { mode: newMode } });
    },
    async handleLogin() {
      try {
        // 模拟登录请求
        await new Promise((resolve) => setTimeout(resolve, 1000)); // 模拟 API 请求延迟
        console.log('Logging in with:', this.username, this.password);
        
        // 登录成功后更新用户状态
        this.$store.dispatch('login', { username: this.username });

        // 登录成功后弹出提醒
        alert('登录成功！');
        
        // 重定向到首页
        this.$router.push('/');
      } catch (error) {
        console.error('Login failed:', error);
        alert('登录失败，请检查用户名和密码。');
      }
    },
    async handleRegister() {
      try {
        // 模拟注册请求
        await new Promise((resolve) => setTimeout(resolve, 1000)); // 模拟 API 请求延迟
        console.log('Registering with:', this.username, this.email, this.password);

        // 注册成功后弹出提醒
        alert('注册成功！');
        
        // 重定向到登录页面
        this.$router.push({ name: 'Auth', query: { mode: 'login' } });
      } catch (error) {
        console.error('Registration failed:', error);
        alert('注册失败，请检查输入信息。');
      }
    }
  }
};
</script>

<style scoped>
.auth-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 20px;
  background-color: #f5f5f5;
}

h1 {
  font-size: 2rem;
  margin-bottom: 20px;
  color: #333;
  text-align: center;
}

form {
  width: 100%;
  max-width: 400px;
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
  font-size: 1rem;
  color: #555;
}

input {
  width: 100%;
  padding: 10px;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  transition: border-color 0.3s ease;
}

input:focus {
  outline: none;
  border-color: #007bff;
}

button {
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

button:hover {
  background-color: #0056b3;
}

p a {
  cursor: pointer;
  color: #007bff;
  text-decoration: underline;
}
</style>