<template>
    <header class="header">
        <nav class="app__nav">
        <ul class="app__tabs">
            <li class="app__tab">
            <router-link to="/textbook" class="nav-link" active-class="active-link">Учебник</router-link>
            </li>
            <li class="app__tab">
            <router-link to="/quiz" class="nav-link" active-class="active-link">Квизы</router-link>
            </li>
            <li class="app__tab">
            <router-link to="/activity" class="nav-link" active-class="active-link">Активность</router-link>
            </li>
        </ul>
        </nav>
        <div class="app__profile">
        <router-link to="/profile" class="nav-link">
            <span class="app__username">{{ props.username }}</span>
        </router-link>
        <router-link to="/profile" class="nav-link">
            <div class="app__avatar"></div>
        </router-link>
        </div>
    </header>
</template>


<script setup>
import { defineProps } from 'vue'

const props = defineProps({
  username: {
    type: String,
    required: true
  }
})

</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #e6f8fc;
  padding: 0 24px;
  height: 64px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  font-size: 1.1rem;
  font-weight: 400;
}

.app__nav {
  flex: 1;
  display: flex;
  justify-content: center;
}

.app__tabs {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
  justify-content: center;
  align-items: center;
}

.app__tab {
  padding: 0 2.5rem;
  cursor: pointer;
}

.app__tab:not(:last-child)::after {
  display: none;
}

.app__tab:not(:first-child) {
  border-left: 1px solid #ccc;
}
.app__tab:hover {
  color: #3182ce;
}
.app__tab--active {
  color: #3182ce;
  border-bottom: 2px solid #3182ce;
}
.app__profile {
  display: flex;
  align-items: center;
  gap: 12px;
}

.app__avatar {
  width: 40px;
  height: 40px;
  background-color: #bbb;
  border-radius: 50%;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
  color: inherit;
  cursor: pointer;
}

.active-link {
    color: #3182ce
}
</style>