<template>
  <div id="app">
    <router-view></router-view> <!-- Здесь отображаются страницы -->
  </div>
</template>
<script>
export default {
  name: 'App',
};
</script>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@100;400;500;700&display=swap');
html, body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  overflow-x: hidden; /* Предотвращает горизонтальную прокрутку */
  background-color: #f8f9fa; /* Убедитесь, что фон совпадает с фоном .content-container */
  font-family: 'Inter', sans-serif;
}
</style>