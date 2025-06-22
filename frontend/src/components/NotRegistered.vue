<script setup>
import { useRouter } from "vue-router"

const router = useRouter()
</script>

<template>
    <div class="modal-overlay">
        <div
            class="modal-content"
            :style="{ 'text-align': 'center' }">
            <h1>Для использования надо зайти в аккаунт</h1>
            <button @click="router.push({ name: 'Registration' })">Зарегистрироваться</button>
            <button @click="router.push({ name: 'Login Page' })">Войти</button>
        </div>
    </div>
</template>


<style scoped>
@import "./grey_style/Main.css";
</style>