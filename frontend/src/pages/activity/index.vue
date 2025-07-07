<template>
  <div class="question-page">
    <invalidUserPanel v-show="user.username == 'Guest'"/>
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
                <input type="checkbox" :value="idx" v-model="correctIndices" />
                <input type="text" v-model="ans.text" class="flex-1 large-input" placeholder="Текст варианта" />
                <button v-if="answers.length &gt; 2" type="button" class="remove-btn" @click="removeAnswer(idx)">×</button>
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

        <button class="btn" type="submit" :disabled="isSubmitDisabled">Создать</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import NavBar from '@/components/NavBar.vue'
import invalidUserPanel from "../../components/NotRegistered.vue"

const chapters = ref([])
const topics   = ref([])
const user     = ref({ username: 'Loading...' })

const creationMode      = ref('question')
const questionChapterId = ref('')
const questionTopicId   = ref('')
const questionType      = ref('open')
const questionText      = ref('')
const criteria          = ref('')
const answers           = ref([{ text: '' }, { text: '' }])
const correctIndices    = ref([])
const chapterName       = ref('')
const topicName         = ref('')
const selectedChapterId = ref('')

const getToken = () => {
  const t = localStorage.getItem('chronoJWTToken')
  if (!t) throw new Error('JWT token not found')
  return t
}

const fetchAll = async () => {
  const token = getToken()
  const headers = { Authorization: `Bearer ${token}` }
  const [chap, top] = await Promise.all([
    axios.get(`http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/topic/get_chapters`, { headers }),
    axios.get(`http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/topic/get_topics`,   { headers })
  ])
  chapters.value = chap.data
  topics.value   = top.data
}

async function fetchUser() {
  try {
    const { data } = await axios.get(`http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/user/me`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    })
    user.value = data
  } catch {
    user.value.username = 'Guest'
  }
}

onMounted(async () => {
  await fetchUser()
  if (user.value.username != 'Guest') {
    await fetchAll()
  }
})

const topicsForQuestion = computed(() => topics.value.filter(t => t.chapter_id === questionChapterId.value))

const isSubmitDisabled = computed(() => {
  if (creationMode.value === 'chapter') return !chapterName.value.trim()
  if (creationMode.value === 'topic')   return !topicName.value.trim() || !selectedChapterId.value

  // question
  if (!questionChapterId.value || !questionTopicId.value || !questionText.value.trim()) return true
  if (questionType.value === 'open') return !criteria.value.trim()
  if (answers.value.length < 2 || answers.value.some(a => !a.text.trim())) return true
  if (correctIndices.value.length === 0) return true
  return false
})

const addAnswer = () => answers.value.push({ text: '' })
const removeAnswer = idx => {
  answers.value.splice(idx, 1)
  correctIndices.value = correctIndices.value.filter(i => i !== idx).map(i => (i > idx ? i - 1 : i))
}

const resetForm = () => {
  questionChapterId.value = questionTopicId.value = ''
  questionType.value = 'open'
  questionText.value = criteria.value = ''
  answers.value      = [{ text: '' }, { text: '' }]
  correctIndices.value = []
  chapterName.value = topicName.value = selectedChapterId.value = ''
}

const onSubmit = async () => {
  const token = getToken()
  const headers = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }

  try {
    if (creationMode.value === 'question') {
      if (questionType.value === 'open') {
        await axios.post(`http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/question/create_ai_question`, {
          description: questionText.value,
          topic_id: questionTopicId.value,
          explanation: criteria.value
        }, { headers })
      } else {
        await axios.post(`http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/question/create_question`, {
          question: {
            description: questionText.value,
            type: correctIndices.length > 1 ? 2 : 1,
            topic_id: questionTopicId.value,
            explanation: ''
          },
          answers: answers.value.map((a, i) => ({ text: a.text, is_correct: correctIndices.value.includes(i) }))
        }, { headers })
      }
    } else if (creationMode.value === 'chapter') {

      await axios.post(
        `http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/topic/create_chapter`,
        { name: chapterName.value },
        { headers }
      )
    } else {
      await axios.post(
        `http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/topic/create_topic`,
        { name: topicName.value, chapter_id: selectedChapterId.value },
        { headers }
      )
    }

    await fetchAll()
    resetForm()
  } catch (e) {
    console.error('Ошибка создания:', e.response?.data || e)
  }
}
</script>


<style scoped>
.question-page {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
.question-page__wrapper {
  flex: 1;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  width: 100%;
}
.question-page__form {
  background: #fff;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  width: 55%;
  max-width: 700px;
}
.question-card__field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.question-card__field label {
  font-weight: 600;
  font-size: 1.1rem;
}
.question-card__field input,
.question-card__field select,
.question-card__field textarea {
  padding: 0.75rem;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 6px;
}
.question-card__field textarea {
  min-height: 140px;
  resize: vertical;
}

.btn {
  padding: 1rem 2rem;
  font-size: 1.1rem;
  font-weight: 600;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  background-color: #2c7a7b;
  color: #fff;
  align-self: center;
  transition: background-color 0.3s;
}

.btn:hover {
  background-color: #276a69;
}
</style>