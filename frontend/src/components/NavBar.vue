<template>
    <header class="header">
        <div class="app__logo-container">
            <router-link to="/" class="nav-link">
                <img src="../../public/ppr_logo.png" alt="Logo" class="app__logo" />
            </router-link>
            </div>

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
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #ffffff;
  padding: 0 24px;
  height: 4rem;
  box-shadow: 0 4px 8px rgba(0,0,0,0.05);
  font-size: 1.1rem;
  font-weight: 400;
  z-index: 2;
}

/* Logo absolutely positioned */
.app__logo-container {
  position: absolute;
  left: 24px;
  top: 50%;
  transform: translateY(-50%);
}

.app__logo {
  height: 2.5rem;
  width: auto;
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
  position: absolute;
  right: 24px;
  top: 50%;
  transform: translateY(-50%);
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
}

.active-link {
  color: #3182ce;
}
</style>