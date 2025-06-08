<script setup>
import { useRouter } from "vue-router";

const router = useRouter();
</script>

<template>
    <div class="top-nav">
        <ul>
            <li @click="router.push({name: 'Welcome'})"><b>Главная</b></li>
            <li @click="router.push({name: 'Schedule Page'})"><b>Расписание</b></li>
            <li @click="router.push({name: 'Deadlines Page'})"><b>Дедлайны</b></li>
            <li @click="router.push({name: 'Profile Page'})"><b>Профиль</b></li>
        </ul>
    </div>
</template>

<style scoped>
@import "./grey_style/NavBar.css";
</style>