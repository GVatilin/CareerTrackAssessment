<template>
  <div>
    <!-- Top navbar -->
    <invalidUserPanel v-show="user.username == 'Guest'"/>
    <NavBar :username="user.username" />
    <div class="quiz-layout">
      <main class="main-content">
        <div v-if="!quizStarted" class="card setup-card">
          <h1 class="page-title">Создать квиз</h1>

          <!-- Выбор главы -->
          <div class="form-field">
            <label>Направление</label>
            <select v-model="params.chapter_id">
              <option :value="null">— Выберите направление —</option>
              <option v-for="c in chapters" :key="c.id" :value="c.id">{{ c.name }}</option>
            </select>
          </div>

          <!-- Выбор темы -->
          <div class="form-field" v-if="filteredTopics.length">
            <label>Тема <span class="text-muted">(необязательно)</span></label>
            <select v-model="params.topic_id">
              <option :value="null">— Любая тема —</option>
              <option v-for="t in filteredTopics" :key="t.id" :value="t.id">{{ t.name }}</option>
            </select>
          </div>

          <!-- Настройка количества вопросов -->
          <div class="form-field inline">
            <label>Обычные вопросы</label>
            <input
              type="number"
              v-model.number="params.n"
              min="0"
              :max="maxCount.total"
            />
            <span class="available-count">
              доступно {{ maxCount.total ?? 0 }}
            </span>
          </div>
          <div class="form-field inline">
            <label>AI-проверяемые</label>
            <input
              type="number"
              v-model.number="params.k"
              min="0"
              :max="maxCount.ai"
            />
            <span class="available-count">
              доступно {{ maxCount.ai ?? 0 }}
            </span>
          </div>
          <div class="form-field inline">
            <label>AI-генерируемые</label>
            <input
              type="number"
              v-model.number="params.ai_compose"
              min="0"
            />
            <!-- для генерируемых вопросов лимит не выводим -->
          </div>

          <button
            class="button-primary w-full"
            @click="startQuiz"
            :disabled="
              loadingQuiz ||
              (!params.chapter_id && !params.topic_id) ||
              params.n > maxCount.total ||
              params.k > maxCount.ai
            "
          >
            {{ loadingQuiz ? 'Составляем квиз' : 'Начать квиз' }}
          </button>
        </div>
      
       <div v-else class="runner-wrapper">
          <div class="card runner-card">
            <div class="question-header">
              <h2 class="question-title">Вопрос {{ currentIndex + 1 }} из {{ total }}</h2>
            </div>

            <div class="question-body">
              <p class="description" v-html="current.description"></p>

              <!-- Варианты ответа -->
              <template v-if="!current.ai">
                <div
                  v-for="ans in current.answers"
                  :key="ans.id"
                  class="answer-option"
                  :class="{
                    selected:   isSelected(ans.id),
                    correct:    showResult && isCorrect(current.id, ans.id),
                    incorrect:  showResult && isSelected(ans.id) && !isCorrect(current.id, ans.id)
                  }"
                >
                  <label>
                    <input
                      :type="current.type === 1 ? 'checkbox' : 'radio'"
                      :name="current.id"
                      :value="ans.id"
                      v-model="userAnswers[current.id]"
                    />
                    <span>{{ ans.text }}</span>
                  </label>
                </div>
              </template>
              
              <!-- AI‑вопрос (свободный ввод) -->
              <!-- AI-вопросы: свободный ввод -->
              <template v-else>
                <!-- если вопрос сгенерированный (id начинается с "gen_") -->
                <textarea
                  v-if="current.id && current.id.startsWith('gen_')"
                  class="answer-input"
                  v-model="userGenAnswers[current.id]"
                  rows="4"
                  placeholder="Ваш ответ..."
                ></textarea>

                <!-- обычный AI-вопрос из базы -->
                <textarea
                  v-else
                  class="answer-input"
                  v-model="userAI[current.id]"
                  rows="4"
                  placeholder="Ваш ответ..."
                ></textarea>
              </template>

            </div>

            <!-- Результат по текущему вопросу -->
            <div v-if="showResult" class="result-section">
              <p v-if="isQuestionRight(current.id) === true"  class="success-message">Правильно!</p>
              <p v-if="isQuestionRight(current.id) === false" class="error-message">Неправильно</p>
            </div>
            <div v-if="showResult" class="result-section">
              <p v-html="getExplanation(current.id)"></p>
            </div>

            <!-- Шаблон: заменили логику вывода кнопок -->
            <div class="nav-buttons">
              <!-- Кнопка «Назад» -->
              <button
                class="button-ghost"
                @click="prev"
                :disabled="currentIndex === 0"
              >
                ← Назад
              </button>

              <button
                v-if="currentIndex < total - 1"
                class="button-ghost"
              @click="next"
              >
                Вперёд →
              </button>

              <!-- «Отправить» (только на последней странице и до результатов) -->
              <button
                v-else-if="!showResult"
                class="button-primary"
                @click="submit"
                :disabled="checkingQuiz"
              >
                {{ checkingQuiz ? 'Проверяем квиз' : 'Отправить' }}
              </button>
            </div>



            <!-- Итог -->
            <div v-if="currentIndex === total - 1 && showResult" class="final-result card mt-4">
              <h3>
                Вы ответили правильно:
                {{ result.correctCount }} из {{ result.totalMc }} ({{ result.scorePercent }}%)
              </h3>
              <p class="ai-review" v-if="result.aiReview" v-html="result.aiReview"></p>
            </div>
          </div>

          <div class="quiz-right-list">
            <button
              class="button-ghost"
              @click="resetQuiz"
            >
              Начать новый квиз
            </button>
            <button
              v-if="pdfUrl != null"
              class="button-ghost"
              @click="openPdfResults"
            >
              Экспортировать результаты тестирования
            </button>
          </div>
        </div>  
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue'
import axios from 'axios'
import NavBar from '@/components/NavBar.vue'
import invalidUserPanel from "../../components/NotRegistered.vue"

// Пользователь (для NavBar)
const user = ref({ username: 'Loading…' })

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

const STORAGE_PARAMS = 'quizParams'
const STORAGE_QUIZ   = 'quizState'
const savedParams = JSON.parse(localStorage.getItem(STORAGE_PARAMS) || '{}')

// Данные 
const chapters = ref([])
const topics = ref([])

// Параметры квиза
const params = reactive({
  n: 5,
  k: 3,
  ai_compose: 2,
  chapter_id: null,
  topic_id: null,
  ...savedParams,
})


// Список тем, фильтрованных по главе
const filteredTopics = computed(() => {
  if (!params.chapter_id) return topics.value
  return topics.value.filter(t => t.chapter_id === params.chapter_id)
})

// Состояния квиза
const quizStarted = ref(false)
const questions = ref([])
const currentIndex = ref(0)
const userAnswers = reactive({})
const userAI = reactive({})
const userGenAnswers = reactive({})
const genQuestions = ref([])
const pdfUrl = ref(null)
const pdfFilename = ref(null)

const showResult = ref(false)
const result = reactive({
  totalMc: 0,
  correctCount: 0,
  scorePercent: 0,
  aiReview: '',
  answers: {},
})

const total = computed(() => questions.value.length)
const current = computed(() => questions.value[currentIndex.value] || {})

const maxCount = reactive({
  total: null,
  ai: null,
})

const loadingQuiz = ref(false)
const checkingQuiz = ref(false)

// Старт квиза
async function startQuiz() {
  loadingQuiz.value = true
  localStorage.removeItem(STORAGE_QUIZ)

  const base = `http://${process.env.VUE_APP_BACKEND_URL}:8080`
  const p = { n: params.n, k: params.k, m: params.ai_compose }
  if (params.chapter_id) p.chapter_id = params.chapter_id
  if (params.topic_id) p.topic_id = params.topic_id

  try {
    const { data } = await axios.get(`${base}/api/v1/question/quiz/get`, { params: p })
    const qs = [
      ...data.questions.map(q => ({ ...q, ai: false })),
      ...data.ai_questions.map(q => ({ ...q, ai: true })),
      ...data.gen_question.map((text, idx) => ({
        id: `gen_${idx}`,
        description: text,
        ai: true,
        type: 0,
        answers: []
      }))
    ]

    resetLocalState()
    questions.value = qs
    quizStarted.value = true
    genQuestions.value = data.gen_question

    console.log(qs)
    
    questions.value.forEach(q => {
      if (q.ai && q.id.startsWith('gen_')) {
        userGenAnswers[q.id] = ''           // для gen_question
      }
      else if (q.ai) {
        userAI[q.id] = ''                   // для ai_questions
      }
      else {
        userAnswers[q.id] = q.type === 1 ? [] : null
      }
    })

    saveQuizState()
  } finally {
      loadingQuiz.value = false
  }
}

// Навигация
function next() {
  if (currentIndex.value < total.value - 1) currentIndex.value++
}
function prev() {
  if (currentIndex.value > 0) currentIndex.value--
}

function isSelected(ansId) {
  const ua = userAnswers[current.value.id]
  return Array.isArray(ua) ? ua.includes(ansId) : ua === ansId
}
function isCorrect(qId, ansId) {
  const qa = result.answers.find(x => x.question_id == qId)
  if (!qa) return false
  return qa.correct_answer_id.includes(ansId)
}
function isQuestionRight(qId) {
  const qa = result.answers.find(x => x.question_id == qId)
  return qa?.is_user_right
}
function getExplanation(qId) {
  const qa = result.answers.find(x => x.question_id == qId)
  return qa?.explanation || ''
}

function getToken() {
  const token = localStorage.getItem('chronoJWTToken')
  if (!token) throw new Error('Token is missing. Please log in.')
  return token
}

async function submit() {
  checkingQuiz.value = true
  const payload = {
    answers: Object.entries(userAnswers).map(([qid, sel]) => ({
      question_id: qid,
      selected_answer_id: Array.isArray(sel) ? sel : sel ? [sel] : [],
    })),
    ai_answers: Object.entries(userAI).map(([qid, txt]) => ({
      question_id: qid,
      text: txt,
    })),
    gen_answers: Object.entries(userGenAnswers).map(([qid, ans]) => ({
      question_id: qid,
      description: questions.value.find(q => q.id === qid).description,
      answer: ans
    }))
  }
  const token = getToken()
  const { data } = await axios.post(`http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/question/quiz/submit`, payload, {
    headers: { Authorization: `Bearer ${token}` },
  })

  result.totalMc = data.total_questions
  result.correctCount = data.total_correct_answers
  result.scorePercent = data.score_percent
  result.aiReview = data.ai_recommendations
  result.answers = data.answers || []
  showResult.value = true
  checkingQuiz.value = false
  saveQuizState()
  await getPdfResults()
}

async function getPdfResults() {
  const resultsData = {
    answers: result.answers,
    ai_recommendations: result.aiReview
  }
  const token = getToken()

  try {
    const response1 = await axios.post(
      `http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/docs/task_results_pdf`,
      resultsData,
      {
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    )
    
    pdfFilename.value = response1.data

    const response2 = await axios.get(
      `http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/docs/task_results_pdf/${pdfFilename.value}`,
      {
        responseType: 'blob',
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    )

    const blob = new Blob([response2.data], { type: 'application/pdf' })
    pdfUrl.value = URL.createObjectURL(blob)
  } catch (error) {
    console.error('Error generating PDF:', error)
  }
}

async function clearPdfResults() {
  pdfUrl.value = null
  const token = getToken()

  try {
    if (pdfFilename.value !== null) {
      await axios.delete(
        `http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/docs/task_results_pdf/${pdfFilename.value}`,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      )
    }
  } catch (error) {
    console.error('Error removing PDF:', error)
  }
  pdfFilename.value = null
}

function openPdfResults() {
  window.open(pdfUrl.value, '_blank');
}

// Функция для запроса количества вопросов
async function updateQuestionCount() {
  // если ни глава, ни тема не выбраны — сбрасываем
  if (!params.chapter_id && !params.topic_id) {
    maxCount.total = null
    maxCount.ai = null
    return
  }

  const base = `http://${process.env.VUE_APP_BACKEND_URL}:8080`
  const query = {}
  if (params.topic_id) {
    query.topic_id = params.topic_id
  } else {
    query.chapter_id = params.chapter_id
  }

  try {
    const { data } = await axios.get(
      `${base}/api/v1/question/quiz/get_question_count`,
      { params: query }
    )
    maxCount.total = data.count
    maxCount.ai    = data.ai_count

    // Не даём params.n и params.k превысить новые лимиты
    if (params.n > data.count) params.n = data.count
    if (params.k > data.ai_count) params.k = data.ai_count
  } catch (e) {
    console.error('Не удалось получить количество вопросов:', e)
  }
}

// При смене chapter_id — сбрасываем topic_id и запрашиваем count
watch(() => params.chapter_id, () => {
  params.topic_id = null
  updateQuestionCount()
})

// При смене topic_id — просто запрашиваем count
watch(() => params.topic_id, updateQuestionCount)

// ─── NEW ───────────────────────────────────────────────────────────────────
function saveQuizState() {
  try {
    if (!quizStarted.value) return
    const plainResult = JSON.parse(JSON.stringify(result))

    localStorage.setItem(STORAGE_QUIZ, JSON.stringify({
      quizStarted:    quizStarted.value,
      questions:      questions.value,
      currentIndex:   currentIndex.value,
      showResult:     showResult.value,
      userAnswers:    JSON.parse(JSON.stringify(userAnswers)),
      userAI:         JSON.parse(JSON.stringify(userAI)),
      userGenAnswers: JSON.parse(JSON.stringify(userGenAnswers)),
      result:         plainResult,
    }))
  } catch (e) {
    console.error('Не удалось сохранить состояние квиза:', e)
  }
}

function restoreQuizState() {
  const saved = localStorage.getItem(STORAGE_QUIZ)
  if (!saved) return
  try {
    const data = JSON.parse(saved)
    if (!data.quizStarted) return

    quizStarted.value  = data.quizStarted
    questions.value    = data.questions || []
    currentIndex.value = data.currentIndex || 0
    showResult.value   = data.showResult || false

    Object.assign(userAnswers,    data.userAnswers    || {})
    Object.assign(userAI,         data.userAI         || {})
    Object.assign(userGenAnswers, data.userGenAnswers || {})
    Object.assign(result,         data.result         || {})
  } catch (e) {
    console.error('Не удалось восстановить состояние квиза:', e)
    localStorage.removeItem(STORAGE_QUIZ)
  }
}

function resetLocalState() {
  questions.value    = []
  currentIndex.value = 0
  quizStarted.value  = false
  showResult.value   = false

  Object.keys(userAnswers)   .forEach(k => delete userAnswers[k])
  Object.keys(userAI)        .forEach(k => delete userAI[k])
  Object.keys(userGenAnswers).forEach(k => delete userGenAnswers[k])

  Object.assign(result, {
    totalMc:          0,
    correctCount:     0,
    scorePercent:     0,
    aiReview:         '',
    answers:          [],
  })
}

// Получаем главы и темы
onMounted(async () => {
  await fetchUser()
  const base = `http://${process.env.VUE_APP_BACKEND_URL}:8080`
  const [chapRes, topRes] = await Promise.all([
    axios.get(`${base}/api/v1/topic/get_chapters`),
    axios.get(`${base}/api/v1/topic/get_topics`),
  ])
  chapters.value = chapRes.data
  topics.value = topRes.data

  restoreQuizState()

  if (params.chapter_id || params.topic_id) {
    updateQuestionCount()
  }
})

onUnmounted(async () => {
  await clearPdfResults() 
})

watch(
  () => params.chapter_id,
  () => {
    params.topic_id = null
  }
)

watch(params,
  () => localStorage.setItem(STORAGE_PARAMS, JSON.stringify(params)),
  { deep: true }
)

watch([
  questions,
  currentIndex,
  userAnswers,
  userAI,
  userGenAnswers,
  showResult,
  result,
  quizStarted,
], saveQuizState, { deep: true })

async function resetQuiz() {
  resetLocalState()
  quizStarted.value = false
  localStorage.removeItem(STORAGE_QUIZ)
  localStorage.removeItem(STORAGE_PARAMS)
  await clearPdfResults()
}
</script>

<style>
:root {
  --color-bg: #ffffff;
  --color-bg-sidebar: #f0f9ff;
  --color-primary: #00aeb5;
  --color-success: #28a745;
  --color-error: #dc3545;
  --color-border: #dddddd;
  --color-text: #333333;
}

.quiz-layout {
  display: flex;
  min-height: 100vh;
  background: var(--color-bg);
  color: var(--color-text);
}
.sidebar {
  width: 220px;
  background: var(--color-bg-sidebar);
  padding: 1rem;
}
.main-content {
  flex: 1;
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem 1rem;
}
.back-btn {
  background: transparent;
  color: var(--color-text);
  border: none;
  font-size: 1.25rem;
  cursor: pointer;
  margin-bottom: 1rem;
}
.sidebar-title {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}
.topics {
  list-style: none;
  padding: 0;
  margin: 0;
}
.topics li {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  cursor: pointer;
}
.topics li.active {
  background: #d7f3f5;
  color: var(--color-primary);
  font-weight: 600;
}
.topics li:hover {
  background: #e9f6f7;
}
body {
  font-size: 16px;
  line-height: 1.5;
}
.page-title {
  font-size: 1.75rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
}
.question-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1rem;
}
.description {
  margin-bottom: 1rem;
}
.card {
  background: var(--color-bg);
  border: 1px solid #ececec;
  border-radius: 6px;
  padding: 1.5rem;
  box-shadow: 0 4px 8px rgba(0,0,0,0.05)
}
.mt-4 {
  margin-top: 1.5rem;
}
.form-field {
  margin-bottom: 1rem;
  display: flex;
  flex-direction: column;
}
.form-field.inline {
  flex-direction: row;
  align-items: center;
  gap: 0.5rem;
}
.form-field label {
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}
.form-field.inline label {
  margin-bottom: 0;
}
.form-field select,
.form-field input[type='number'] {
  flex: 1;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: 1rem;
}

.button-primary {
  background: #38a169;
  color: #fff;
  border: none;
  border-radius: 4px;
  padding: 0.5rem 1rem;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s;
}
.button-primary:hover {
  background: #2f855a;
}
.button-primary:disabled {
  opacity: 0.6;
  cursor: default;
}
.button-ghost {
  background: transparent;
  color: var(--color-text);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: background 0.2s;
}
.button-ghost:hover:not(:disabled) {
  background: #f5f5f5;
}
.button-ghost:disabled {
  opacity: 0.5;
  cursor: default;
}
.w-full {
  width: 100%;
}

.question-body {
  margin-bottom: 1rem;
}
.answer-option {
  position: relative;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  padding: 0.5rem 0.75rem;
  margin-bottom: 0.5rem;
  cursor: pointer;
  transition: border 0.2s, background 0.2s;
}
.answer-option input {
  margin-right: 0.5rem;
}
.answer-option.selected {
  border-color: var(--color-primary);
  background: #e8f7f9;
}
.answer-option.correct {
  border-left: 4px solid var(--color-success);
}
.answer-option.incorrect {
  border-left: 4px solid var(--color-error);
}

.answer-input {
  width: 100%;
  max-width: 100%;
  padding: 0.5rem 0.75rem;
  font-size: 1rem;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  resize: vertical;
  box-sizing: border-box;
}
.answer-input:focus {
  border-color: var(--color-primary);
  outline: none;
}

.result-section {
  margin-top: 1rem;
}
.success-message {
  color: var(--color-success);
  font-weight: 600;
}
.error-message {
  color: var(--color-error);
  font-weight: 600;
}
.explanation {
  background: #f9f9f9;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 1rem;
  margin-top: 0.75rem;
}

.nav-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 1.5rem;
}
.submit-area {
  margin-top: 1.5rem;
}

@media (max-width: 768px) {
  .sidebar {
    display: none;
  }
  .main-content {
    padding: 1rem;
  }
  .nav-buttons {
    flex-direction: column;
    gap: 0.5rem;
  }
  .button-ghost {
    width: 100%;
  }
}

.form-field.inline label {
  flex: 0 0 8rem; /* фиксированная ширина метки для выравнивания */
  margin: 0;
  padding-right: 0.5rem;
}

.form-field.inline select {
  flex: 1;
}

.form-field.inline input[type='number'] {
  flex: 0 0 auto;
  width: 2.3rem;
}

.available-count {
  margin-left: 0.5rem;
  font-size: 0.875rem;
  color: #666666;
  white-space: nowrap;
}

.card.setup-card,
.card.runner-card {
  min-height: 60%;
}

.card.setup-card,
.card.runner-card {
  display: flex;
  flex-direction: column;
}

.card.setup-card .button-primary {
  margin-top: auto;
}

.card.runner-card .nav-buttons,
.card.runner-card .submit-area {
  margin-top: auto;
}

.card.runner-card .nav-buttons,
.card.runner-card .submit-area {
  background: var(--color-bg);
  padding-top: 1rem;
  border-top: 1px solid var(--color-border);
}

.nav-buttons .button-ghost {
  padding: 0.5rem 1rem;
  font-size: 1rem;
}

.nav-buttons .button-ghost,
.nav-buttons .button-primary {
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-buttons button {
  min-height: 2.5rem;
}

.nav-buttons .button-primary {
  min-width: 12rem;
}


.runner-wrapper {
  position: relative;
  width: 100%;
}

/* кнопка абсолютно позиционируется правее карточки и НЕ влияет на её размер */
.quiz-right-list {
  position: absolute;
  top: 0;
  left: calc(100% + 0.7rem);   /* справа на 1 rem от края карточки */
  white-space: nowrap;
  display: flex;
  gap: 1rem;
  flex-direction: column;
  font-size: 1rem;       /* чуть больший текст */
  border-radius: 6px;
}

.card.runner-card {
  min-height: 60vh;   /* 60 % высоты окна вместо относительных 60 % родителя */
}

</style>
