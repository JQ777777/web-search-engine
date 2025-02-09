<template>
    <div class="html-snapshot">
      <button @click="goBack" class="back-button">返回</button>
      <iframe v-if="htmlFilePath" :src="htmlFilePath" width="100%" height="800px" frameborder="0"></iframe>
      <p v-else>网页快照加载失败，请稍后再试。</p>
    </div>
  </template>
  
  <script>
  export default {
    props: {
      htmlFilePath: String
    },
    mounted() {
        console.log('Route params:', this.$route.params); // 检查所有路由参数
        console.log('Received htmlFilePath:', this.htmlFilePath); // 调试输出
    },
    methods: {
      goBack() {
        this.$router.go(-1); // 返回上一页
      }
    }
  };
  </script>
  
  <style scoped>
  .html-snapshot {
    padding: 20px;
  }
  
  .back-button {
    margin-bottom: 20px;
    padding: 10px 20px;
    font-size: 1rem;
    color: #fff;
    background-color: #007bff;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.3s ease;
  }
  
  .back-button:hover {
    background-color: #0056b3;
  }
  </style>