<template>
  <div class="question-page">
    <NavBar :username="user.username" />

    <div class="question-page__wrapper">
      <form class="question-page__form" @submit.prevent="onSubmit">
        <div class="question-card__field">
          <label for="creationMode">Что создать:</label>
          <select id="creationMode" v-model="creationMode">
            <option value="question">Вопрос</option>
            <option value="chapter">Раздел</option>
            <option value="topic">Тему</option>
          </select>
        </div>

        <template v-if="creationMode === 'question'">
          <div class="question-card__field">
            <label for="qChapter">Раздел:</label>
            <select id="qChapter" v-model="questionChapterId" @change="questionTopicId = ''">
              <option disabled value="">-- выберите раздел --</option>
              <option v-for="chap in chapters" :key="chap.id" :value="chap.id">{{ chap.name }}</option>
            </select>
          </div>
          <div v-if="questionChapterId" class="question-card__field">
            <label for="qTopic">Тема:</label>
            <select id="qTopic" v-model="questionTopicId">
              <option disabled value="">-- выберите тему --</option>
              <option v-for="t in topicsForQuestion" :key="t.id" :value="t.id">{{ t.name }}</option>
            </select>
          </div>
          <div class="question-card__field">
            <label for="questionType">Тип вопроса:</label>
            <select id="questionType" v-model="questionType">
              <option value="open">С открытым ответом</option>
              <option value="choice">С выбором ответа</option>
            </select>
          </div>
          <div class="question-card__field">
            <label for="questionText">Текст вопроса:</label>
            <textarea id="questionText" v-model="questionText" class="large-field" placeholder="Введите текст вопроса"></textarea>
          </div>
          <div v-if="questionType === 'open'" class="question-card__field">
            <label for="criteria">Пояснение / критерии:</label>
            <textarea id="criteria" v-model="criteria" class="large-field" placeholder="Введите пояснение или критерии"></textarea>
          </div>
          <template v-else>
            <div class="question-card__field" v-for="(ans, idx) in answers" :key="idx">
              <label>Вариант {{ idx + 1 }}</label>
              <div class="answer-row">
                <input type="radio" :name="'correctRadio'" :value="idx" v-model="correctIndex" />
                <input type="text" v-model="ans.text" class="large-input flex-1" placeholder="Текст варианта" />
                <button type="button" class="remove-btn" @click="removeAnswer(idx)" v-if="answers.length &gt; 2">×</button>
              </div>
            </div>
            <button type="button" class="btn btn--secondary" @click="addAnswer">Добавить вариант</button>
          </template>
        </template>

        <div v-if="creationMode === 'chapter'" class="question-card__field">
          <label for="chapterName">Название раздела:</label>
          <input id="chapterName" v-model="chapterName" class="large-input" placeholder="Введите название раздела" />
        </div>

        <template v-if="creationMode === 'topic'">
          <div class="question-card__field">
            <label for="topicName">Название темы:</label>
            <input id="topicName" v-model="topicName" class="large-input" placeholder="Введите название темы" />
          </div>
          <div class="question-card__field">
            <label for="selectedChapter">Выберите раздел:</label>
            <select id="selectedChapter" v-model="selectedChapterId" class="large-input">
              <option disabled value="">-- выберите раздел --</option>
              <option v-for="chap in chapters" :key="chap.id" :value="chap.id">{{ chap.name }}</option>
            </select>
          </div>
        </template>

        <button type="submit" class="btn" :disabled="isSubmitDisabled">Создать</button>
      </form>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, onMounted, computed } from 'vue'
import axios from 'axios'
import NavBar from '@/components/NavBar.vue'

export default defineComponent({
  components: { NavBar },
  setup() {
    const user = ref({ username: '...' })
    const chapters = ref([])
    const topics = ref([])

    const creationMode = ref('question')
    const questionChapterId = ref('')
    const questionTopicId = ref('')
    const questionType = ref('open')
    const questionText = ref('')
    const criteria = ref('')
    const answers = ref([{ text: '' }, { text: '' }])
    const correctIndex = ref(0)

    const chapterName = ref('')
    const topicName = ref('')
    const selectedChapterId = ref('')

    const getToken = () => localStorage.getItem('chronoJWTToken') || ''

    const fetchAll = async () => {
      const token = getToken()
      const [chap, top] = await Promise.all([
        axios.get(`http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/topic/get_chapters`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/topic/get_topics`, { headers: { Authorization: `Bearer ${token}` } })
      ])
      chapters.value = chap.data
      topics.value = top.data
    }

    onMounted(fetchAll)

    const topicsForQuestion = computed(() => topics.value.filter(t => t.chapter_id === questionChapterId.value))

    const isSubmitDisabled = computed(() => {
      if (creationMode.value === 'chapter') return !chapterName.value.trim()
      if (creationMode.value === 'topic') return !topicName.value.trim() || !selectedChapterId.value
      if (!questionChapterId.value || !questionTopicId.value || !questionText.value.trim()) return true
      if (questionType.value === 'open') return !criteria.value.trim()
      if (answers.value.some(a => !a.text.trim()) || answers.value.length < 2) return true
      return false
    })

    const addAnswer = () => answers.value.push({ text: '' })
    const removeAnswer = i => { answers.value.splice(i, 1); if (correctIndex.value >= answers.value.length) correctIndex.value = 0 }

    const onSubmit = () => alert('Здесь логика отправки (сокращена в примере)')

    return {
      user,
      chapters,
      topicsForQuestion,
      creationMode,
      questionChapterId,
      questionTopicId,
      questionType,
      questionText,
      criteria,
      answers,
      correctIndex,
      chapterName,
      topicName,
      selectedChapterId,
      isSubmitDisabled,
      addAnswer,
      removeAnswer,
      onSubmit
    }
  }
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

* { box-sizing: border-box; }
body { margin: 0; font-family: 'Inter', sans-serif; color: #2d3748; background:#f7fbfd; }

.question-page { display:flex; flex-direction:column; min-height:100vh; }
.question-page__wrapper { flex:1; display:flex; align-items:center; justify-content:center; padding:2rem; }

.question-page__form { background:#fff; border-radius:12px; box-shadow:0 4px 12px rgba(0,0,0,.05); width:100%; max-width:720px; padding:2rem 2.5rem; display:flex; flex-direction:column; gap:1.5rem; }

.question-card__field { display:flex; flex-direction:column; gap:0.5rem; }
.question-card__field label { font-weight:600; }

.question-card__field input,
.question-card__field select,
.question-card__field textarea { padding:0.9rem 1rem; border:1px solid #cbd5e0; border-radius:8px; font-size:1rem; }
.question-card__field textarea { min-height:140px; resize:vertical; }

.answer-row { display:flex; align-items:center; gap:0.75rem; }
.flex-1 { flex:1 1 auto; }
.remove-btn { background:transparent; border:none; font-size:1.25rem; color:#c53030; cursor:pointer; }

.btn { background:#2c7a7b; color:#fff; border:none; padding:0.9rem 2rem; border-radius:8px; font-weight:600; cursor:pointer; transition:background .2s; }
.btn:hover:not(:disabled) { background:#276a69; }
.btn:disabled { opacity:.5; cursor:not-allowed; }
.btn--secondary { background:#e6f8fc; color:#2d3748; padding:0.75rem 1.25rem; margin-top:-0.5rem; }
.btn--secondary:hover:not(:disabled) { background:#c4dee4; }
</style>
