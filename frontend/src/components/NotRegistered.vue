<script setup>
import { useRouter } from "vue-router"

const router = useRouter()
</script>

<template>
    <div class="modal-overlay">
        <div
            class="modal-content"
            :style="{ 'text-align': 'center' }">
            <h1 :style="{ 'font-size': '50px' }">
                Для использования надо зайти в аккаунт
            </h1>
            <ul class="app__tabs">
                <li class="app__tab">
                    <router-link to="/login" class="nav-link login-buttons" active-class="active-link">
                        Войти
                    </router-link>
                </li>
                <li class="app__tab">
                    <router-link to="/registration" class="nav-link login-buttons" active-class="active-link">
                        Зарегистрироваться
                    </router-link>
                </li>
            </ul>
        </div>
    </div>
</template>


<style scoped>
@import "./grey_style/Main.css";

.login-buttons {
    font-size: 30px;
}

</style>