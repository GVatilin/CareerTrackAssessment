<template>
  <div class="auth-page">
    <NavBar :username="user.username" />
    <div class="auth-page__content">
      <div class="auth-card">
        <h2 class="auth-card__title">Смена пароля</h2>



        <form v-if="method === 'old'" @submit.prevent="changeViaOld">
          <div class="input-group">
            <label for="oldPassword">Старый пароль</label>
            <input id="oldPassword" type="password" v-model="oldPassword" required />
          </div>
          <div class="input-group">
            <label for="newPassword">Новый пароль</label>
            <input id="newPassword" type="password" v-model="newPassword" required />
          </div>
          <div class="input-group">
            <label for="confirmPassword">Подтвердите пароль</label>
            <input id="confirmPassword" type="password" v-model="confirmPassword" required />
          </div>
          <button type="submit" class="button-primary" :disabled="loading">
            {{ loading ? 'Сохранение…' : 'Сменить пароль' }}
          </button>
        </form>

        <!-- by mail -->
        <form v-else @submit.prevent="sendResetLink">
          <div class="input-group">
            <label for="email">Email</label>
            <input id="email" type="email" v-model="email" required />
          </div>
          <button type="submit" class="button-primary" :disabled="loading">
            {{ loading ? 'Отправка…' : 'Получить ссылку' }}
          </button>
        </form>

        <p v-if="message" :class="['message', messageType]">{{ message }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import NavBar from '../../components/NavBar.vue'

const user = ref({ username: '' })

const method = ref('old')
const oldPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const email = ref('')
const loading = ref(false)
const message = ref('')
const messageType = ref('')


const getToken = () => localStorage.getItem('chronoJWTToken')

async function changeViaOld () {
  if (newPassword.value !== confirmPassword.value) {
    showMessage('Пароли не совпадают.', 'error')
    return
  }

  await request(
    () => axios.put(
      `http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/settings/update_password`,
      { oldpassword: oldPassword.value, password: newPassword.value },
      { headers: { Authorization: `Bearer ${getToken()}` } }
    ),
    'Пароль успешно изменён.'
  )

  oldPassword.value = ''
  newPassword.value = ''
  confirmPassword.value = ''
}

async function sendResetLink () {
  await request(
    () => axios.put(
      `http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/auth/password_reset`,
      { email: email.value }
    ),
    'Ссылка отправлена на вашу почту.'
  )

  email.value = ''
}
async function request (fn, successText) {
  loading.value = true
  showMessage('')
  try {
    await fn()
    showMessage(successText, 'success')
  } catch (err) {
    showMessage(err?.response?.data?.message || 'Произошла ошибка.', 'error')
  } finally {
    loading.value = false
  }
}

function showMessage (text, type = '') {
  message.value = text
  messageType.value = type
}
</script>

<style scoped>
.auth-page {
  font-family: var(--font-family-base);
  background: var(--bg-light);
  min-height: 100vh;
}

.auth-page__content {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
}

.auth-card {
  background: #fff;
  border-radius: 0.75rem;
  padding: 2rem;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.auth-card__title {
  text-align: center;
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  color: var(--text-dark);
  font-family: var(--font-family-heading);
}

/***** TABS *****/
.auth-tabs {
  display: flex;
  justify-content: space-around;
  margin-bottom: 1.5rem;
}

.auth-tab-button {
  flex: 1;
  padding: 0.5rem 0;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  font: 600 1rem/1 Onest, var(--font-family-base), sans-serif;
  cursor: pointer;
  transition: border-color 0.2s;
  color: var(--text-dark);
}

.auth-tab-button.active {
  border-color: var(--primary, #3b82f6);
  color: var(--primary, #3b82f6);
}

.input-group {
  margin-bottom: 1rem;
  display: flex;
  flex-direction: column;
}

.input-group label {
  margin-bottom: 0.5rem;
  font: 500 0.875rem/1 Onest, var(--font-family-base), sans-serif;
  color: var(--text-medium);
}

.input-group input {
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font: 400 1rem/1.4 Onest, var(--font-family-base), sans-serif;
}

.button-primary {
  width: 100%;
  padding: 0.75rem;
  background: var(--primary, #3b82f6);
  color: #fff;
  border: none;
  border-radius: 4px;
  font: 600 1rem/1 Onest, var(--font-family-base), sans-serif;
  cursor: pointer;
  transition: opacity 0.2s, filter 0.2s;
  opacity: 1;
}

.button-primary:hover {
  opacity: 0.9;
}

.button-primary:disabled {
  background: var(--primary, #3b82f6);
  opacity: 0.6;
  cursor: not-allowed;
  filter: grayscale(20%);
}
</style>
