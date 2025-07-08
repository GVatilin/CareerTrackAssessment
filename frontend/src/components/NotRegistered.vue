<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<template>
  <div class="modal-overlay">
    <div class="modal-content text-center">
      <h1 class="title">Для использования надо зайти в аккаунт</h1>
      <ul class="tabs">
        <li class="tab">
          <router-link to="/login" class="btn" active-class="active-link">Войти</router-link>
        </li>
        <li class="tab">
          <router-link to="/registration" class="btn" active-class="active-link">Зарегистрироваться</router-link>
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(4px);
  z-index: 1000;
}

.modal-content {
  background: #ffffff;
  border-radius: 1.5rem;
  padding: 2.5rem 3rem;
  max-width: 480px;
  width: 100%;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.05);
}

.title {
  font-size: 2rem;
  font-weight: 600;
  margin-bottom: 2rem;
  color: #333;
  line-height: 1.3;
}

.tabs {
  display: flex;
  gap: 1.5rem;
  list-style: none;
  padding: 0;
  margin: 0;
  justify-content: center;
}

.btn {
  display: inline-block;
  padding: 0.75rem 2rem;
  font-size: 1.125rem; /* 18px */
  font-weight: 500;
  color: #333;
  text-decoration: none;
  background: #f7f7f7;
  border: 2px solid transparent;
  border-radius: 9999px;
  transition: all 0.2s ease;
}

.btn:hover,
.btn:focus {
  background: #ffffff;
  border-color: #e2e2e2;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
}

</style>
