<template>
  <div class="quiz-page">
    <!-- Шаг 1: выбор темы и параметров -->
    <div v-if="!quizStarted" class="setup">
      <h2>Создать квиз</h2>
      <div class="field">
        <label>Тема:</label>
        <select v-model="params.topic_id">
          <option v-for="t in topics" :key="t.id" :value="t.id">{{ t.name }}</option>
        </select>
      </div>
      <div class="field">
        <label>Обычные вопросы:</label>
        <input type="number" v-model.number="params.n" min="0" />
      </div>
      <div class="field">
        <label>AI-проверяемые вопросы:</label>
        <input type="number" v-model.number="params.k" min="0" />
      </div>
      <div class="field">
        <label>AI-генерируемые вопросы:</label>
        <input type="number" v-model.number="params.ai_compose" min="0" />
        <small>(передаётся в GET как ai_compose, бэкенд пока игнорирует)</small>
      </div>
      <button @click="startQuiz" class="btn">Начать квиз</button>
    </div>

    <!-- Шаг 2: прохождение -->
    <div v-else class="runner">
      <h3>Вопрос {{ currentIndex+1 }} из {{ total }}</h3>
      <div class="question">
        <p v-html="current.description"></p>

        <!-- Обычные вопросы (с вариантами) -->
        <div v-if="!current.ai">
          <div
            v-for="ans in current.answers"
            :key="ans.id"
            :class="[
              'answer',
              { selected: isSelected(ans.id),
                correct: showResult && isCorrect(current.id, ans.id),
                incorrect: showResult && !isCorrect(current.id, ans.id) }
              ]"
          >
            <label>
              <input
                :type="current.type===1?'checkbox':'radio'"
                :name="current.id"
                :value="ans.id"
                v-model="userAnswers[current.id]"
              />
              {{ ans.text }}
            </label>
          </div>
        </div>

        <!-- AI-вопросы (свободный ввод) -->
        <div v-else>
          <textarea
            v-model="userAI[current.id]"
            placeholder="Ваш ответ..."
            rows="4"
            class="ai-input"
          ></textarea>
        </div>
      </div>

      <div class="nav">
        <button @click="prev" :disabled="currentIndex===0">← Назад</button>
        <button @click="next" :disabled="currentIndex>=total-1">Вперед →</button>
      </div>

      <div v-if="currentIndex===total-1" class="submit-wrap">
        <button @click="submit" class="btn submit">Отправить</button>
      </div>

      <!-- Шаг 3: результаты -->
      <div v-if="showResult" class="results">
        <h4>Вы ответили правильно: {{ result.correctCount }} из {{ total }}</h4>
        <h5>AI-Review:</h5>
        <p class="ai-review">{{ result.aiReview }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import axios from 'axios'

// список тем
const topics = ref([])
// параметры квиза
const params = reactive({ n: 5, k: 3, ai_compose: 2, topic_id: null })
// подгрузить темы
onMounted(async () => {
  const { data } = await axios.get('/api/v1/topic/get_topics')
  topics.value = data
  if (data.length) params.topic_id = data[0].id
})

const quizStarted = ref(false)
const questions = ref([])
const currentIndex = ref(0)

// ответы пользователя
const userAnswers = reactive({})   // для вопросов с вариантами
const userAI = reactive({})        // для AI-вопросов свободный текст

// после сабмита:
const showResult = ref(false)
const result = reactive({ correctCount:0, aiReview:'', answers: [] })

// запуск: получить список вопросов
async function startQuiz() {
  const p = { n: params.n, k: params.k, topic_id: params.topic_id }
  // даже если бэкенд пока не умеет, передаём ai_compose
  if (params.ai_compose) p.ai_compose = params.ai_compose

  const { data } = await axios.get('/api/v1/question/quiz/get', { params: p })
  // склеиваем обычные и AI-вопросы, помечаем флагом ai
  const qs = [
    ...data.questions.map(q=>({ ...q, ai: false })),
    ...data.ai_questions.map(q=>({ ...q, ai: true }))
  ]
  questions.value = qs
  quizStarted.value = true
  // инициализируем стейт ответов
  qs.forEach(q=>{
    if (q.ai) userAI[q.id] = ''
    else userAnswers[q.id] = q.type===1 ? [] : null
  })
}

// навигация
const total = computed(()=>questions.value.length)
const current = computed(()=>questions.value[currentIndex.value]||{})

function next()  { if (currentIndex.value<total.value-1) currentIndex.value++ }
function prev()  { if (currentIndex.value>0) currentIndex.value-- }

// вспомогательные для подсветки
function isSelected(ansId) {
  const ua = userAnswers[current.value.id]
  return Array.isArray(ua) ? ua.includes(ansId) : ua===ansId
}
function isCorrect(qId, ansId) {
  const qa = result.answers.find(x=>x.question_id===qId)
  if (!qa) return false
  return qa.correct_answer_id.includes(ansId)
}

const getToken = () => {
  const token = localStorage.getItem('chronoJWTToken')
  if (!token) throw new Error('Token is missing. Please log in.')
  return token
}

// финальный сабмит
async function submit() {
  const payload = {
    answers: Object.entries(userAnswers).map(([qid, sel])=>({
      question_id: qid,
      selected_answer_id: Array.isArray(sel)? sel : sel?[sel]:[]
    })),
    ai_answers: Object.entries(userAI).map(([qid, txt])=>({
      question_id: qid,
      text: txt
    }))
  }
  const token = getToken()
  const { data } = await axios.post('/api/v1/question/quiz/submit', payload, { headers: { Authorization: `Bearer ${token}` } })
  // ожидаем в ответе { correctCount, aiReview, answers: [{question_id, correct_answer_id:[], is_user_right}, …] }
  result.correctCount = data.correct_mc
  result.aiReview    = data.ai_answers_received
  result.answers     = data.answers
  showResult.value   = true
}
</script>

<style scoped>
.quiz-page { max-width:600px; margin:40px auto; font-family:sans-serif; }
.field { margin:10px 0; }
.btn { padding:8px 16px; background:#2ecc71; color:#fff; border:none; cursor:pointer; }
.submit { background:#3498db; }
.question { background:#f9f9f9; padding:16px; border-radius:4px; }
.answer { padding:6px; margin:4px 0; border:1px solid #ddd; border-radius:3px; }
.answer.selected { background:#eef; }
.answer.correct { border-left:4px solid green; }
.answer.incorrect { border-left:4px solid red; }
.nav { margin:12px 0; }
.ai-input { width:100%; }
.results { margin-top:20px; background:#fffbe6; padding:16px; border-radius:4px; }
.ai-review { font-style:italic; }
</style>
