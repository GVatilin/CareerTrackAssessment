<template>
  <div class="app">
    <NavBar :username="user.username" />

    <div class="app__body">
      <button class="sidebar-toggle" @click="toggleSidebar"
      :class="showSidebar ? 'sidebar-toggle--visible' : 'sidebar-toggle--hidden'">
        <svg v-if="showSidebar" width="12" height="12" viewBox="0 0 8 8">
          <!-- «<=»-стрелка — указываем влево -->
          <path d="M6,0 L2,4 L6,8" stroke="#333" fill="none" stroke-width="1"/>
        </svg>
        <svg v-else width="12" height="12" viewBox="0 0 8 8">
          <!-- «=>»-стрелка — указываем вправо -->
          <path d="M2,0 L6,4 L2,8" stroke="#333" fill="none" stroke-width="1"/>
        </svg>
      </button>

      <!-- Sidebar -->
      <aside
        :class="['sidebar', { 'sidebar--hidden': !showSidebar }]"
      >
        <div
          v-for="chapter in chapters"
          :key="chapter.id"
          class="sidebar__chapter"
        >
          <h2 @click="toggleChapter(chapter.id)" class="sidebar__chapter-title">
            {{ chapter.name }}
          </h2>
          <div v-if="isChapterOpen(chapter.id)" class="sidebar__topics">
            <div
              v-for="topic in getTopicsByChapter(chapter.id)"
              :key="topic.id"
              class="sidebar__topic"
            >
              <h3 @click="toggleTopic(topic.id)" class="sidebar__topic-title">
                {{ topic.name }}
              </h3>
              <ul
                v-if="isTopicOpen(topic.id)"
                class="sidebar__questions"
              >
                <li
                  v-for="question in getQuestionsByTopic(topic.id)"
                  :key="question.id"
                  class="sidebar__question"
                >
                  <button
                    @click="selectQuestion(question)"
                    class="sidebar__question-btn"
                  >
                    {{ question.description }}
                  </button>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </aside>

      <!-- Main content -->
      <main class="main">
        <div v-if="selectedQuestion" class="question">
          <h2 class="question__title">
            {{ selectedQuestion.description }}
          </h2>

          <ul v-if="answers.length" class="question__answers">
            <li
              v-for="answer in answers"
              :key="answer.id"
              :class="[
                'question__answer',
                correctAnswers?.includes(answer.id) && 'question__answer--correct',
                userAnswers?.includes(answer.id) && !correctAnswers?.includes(answer.id) && 'question__answer--wrong'
              ]"
            >
              <label class="question__label">
                <input
                  v-if="selectedQuestion.type === 0"
                  class="question__input"
                  type="radio"
                  :value="answer.id"
                  v-model="selectedAnswer"
                  :disabled="resultStatus !== null"
                />
                <input
                  v-else
                  class="question__input"
                  type="checkbox"
                  :value="answer.id"
                  v-model="selectedAnswers"
                  :disabled="resultStatus !== null"
                />
                <span>{{ answer.text }}</span>
              </label>
            </li>
          </ul>
          <p v-else class="question__empty">Ответы не найдены.</p>

          <div class="question__actions">
            <button
              @click="resultStatus === null ? submitAnswers() : resetQuestion()"
              :class="['btn', resultStatus === null ? 'btn--submit' : 'btn--reset']"
              :disabled="resultStatus === null
                ? (selectedQuestion.type === 0 && !selectedAnswer) ||
                  (selectedQuestion.type !== 0 && !selectedAnswers.length)
                : false"
            >
              {{ resultStatus === null ? 'Ответить' : 'Ответить ещё раз' }}
            </button>

            <button
              class="btn btn--show-answer"
              @click="toggleExplanation"
            >
              <svg width="16" height="16" viewBox="0 0 24 24">
                <line x1="4" y1="8" x2="12" y2="16" stroke="#333" stroke-width="2" />
                <line x1="20" y1="8" x2="12" y2="16" stroke="#333" stroke-width="2" />
              </svg>
              <span>{{ showExplanation ? 'Скрыть ответ' : 'Показать ответ' }}</span>
            </button>
          </div>

          <div v-if="showExplanation" class="question__explanation">
            {{ selectedQuestion.explanation }}
          </div>
          
          <div class="question__nav">
            <button
              @click="prevQuestion"
              :disabled="!hasPrev"
              class="btn btn--nav"
            >
              Предыдущий вопрос
            </button>
            <button
              @click="nextQuestion"
              :disabled="!hasNext"
              class="btn btn--nav"
            >
              Следующий вопрос
            </button>
          </div>
        </div>

        <div v-else class="main__placeholder">
          Выберите вопрос слева, чтобы начать тест.
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import NavBar from "../../components/NavBar.vue";

const user = ref({ username: "Loading..." });
const chapters = ref([])
const topics = ref([])
const questions = ref([])

const openChapters = ref([])
const openTopics = ref([])

const selectedQuestion = ref(null)
const answers = ref([])
const selectedAnswer = ref(null)
const selectedAnswers = ref([])
const userAnswers = ref([])
const correctAnswers = ref([])
const resultStatus = ref(null)  // null = не проверено, true/false после проверки
const resultMessage = ref('')
const showSidebar = ref(true)  
const showExplanation = ref(false)

const getToken = () => {
  const token = localStorage.getItem('chronoJWTToken')
  if (!token) throw new Error('Token is missing. Please log in.')
  return token
}

const getUser = async () => {
  try {
    const token = getToken()
    const { data } = await axios.get(
      `http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/user/me`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      },
    )
    return data
  } catch {
    return -1
  }
}

const fetchUser = async () => {
  user.value = await getUser();
};

const fetchChapters = () =>
  axios.get(
    `http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/topic/get_chapters`,
  )
const fetchTopics = () =>
  axios.get(
    `http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/topic/get_topics`,
  )
const fetchQuestions = () =>
  axios.get(
    `http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/question/get_questions`,
  )


const fetchAnswers = async questionId => {
  try {
    const token = getToken()
    console.log('JWT token is', token)
    const { data } = await axios.post(
      `http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/question/get_answers_to_question`,
      { question_id: questionId },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      },
    )
    answers.value = data
  } catch (err) {
    answers.value = []
  }
}


const loadData = async () => {
  try {
    const [chapRes, topicRes, quesRes] = await Promise.all([
      fetchChapters(),
      fetchTopics(),
      fetchQuestions(),
      getUser(),
      fetchUser(),
    ])

    chapters.value = chapRes.data
    topics.value = topicRes.data

    questions.value = quesRes.data.map(q => ({
      ...q,
      answers: q.answers || [],
    }))
  } catch (err) {
    console.error('Ошибка при загрузке данных:', err)
  }
}


const getTopicsByChapter = chapterId =>
  topics.value.filter(t => t.chapter_id === chapterId)

const getQuestionsByTopic = topicId =>
  questions.value.filter(q => q.topic_id === topicId)


const toggleChapter = id => {
  const idx = openChapters.value.indexOf(id)
  idx > -1 ? openChapters.value.splice(idx, 1) : openChapters.value.push(id)
}
const isChapterOpen = id => openChapters.value.includes(id)

const toggleTopic = id => {
  const idx = openTopics.value.indexOf(id)
  idx > -1 ? openTopics.value.splice(idx, 1) : openTopics.value.push(id)
}
const isTopicOpen = id => openTopics.value.includes(id)


const selectQuestion = async question => {
  selectedQuestion.value = question
  selectedAnswer.value = null
  showExplanation.value = false
  await fetchAnswers(question.id)
}

const submitAnswers = async () => {
  // Prepare payload
  userAnswers.value =
    selectedQuestion.value.type === 0
      ? [selectedAnswer.value]
      : [...selectedAnswers.value]

  try {
    const token = getToken()
    const { data } = await axios.post(
      `http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/question/check_user_answers`,
      {
        question_id: selectedQuestion.value.id,
        selected_answer_id: userAnswers.value
      },
      { headers: { Authorization: `Bearer ${token}` } }
    )

    // Ответ от сервера: { is_correct: bool, correct_answer_ids: UUID[] }
    resultStatus.value = data.is_correct
    resultMessage.value = data.is_correct ? 'Правильно!' : 'Неправильно'
    correctAnswers.value = data.correct_answer_id
  } catch (err) {
    console.error('Ошибка при проверке ответов:', err)
  }
}

// Computed list of topics ordered by chapters
const orderedTopics = computed(() =>
  chapters.value.flatMap(chap =>
    topics.value.filter(t => t.chapter_id === chap.id)
  )
)

// Navigation state
const hasNext = computed(() => {
  if (!selectedQuestion.value) return false
  const currentQs = getQuestionsByTopic(selectedQuestion.value.topic_id)
  const idx = currentQs.findIndex(q => q.id === selectedQuestion.value.id)
  if (idx < currentQs.length - 1) return true
  const topicIdx = orderedTopics.value.findIndex(
    t => t.id === selectedQuestion.value.topic_id
  )
  for (let i = topicIdx + 1; i < orderedTopics.value.length; i++) {
    if (getQuestionsByTopic(orderedTopics.value[i].id).length) return true
  }
  return false
})

const hasPrev = computed(() => {
  if (!selectedQuestion.value) return false
  const currentQs = getQuestionsByTopic(selectedQuestion.value.topic_id)
  const idx = currentQs.findIndex(q => q.id === selectedQuestion.value.id)
  if (idx > 0) return true
  const topicIdx = orderedTopics.value.findIndex(
    t => t.id === selectedQuestion.value.topic_id
  )
  for (let i = topicIdx - 1; i >= 0; i--) {
    if (getQuestionsByTopic(orderedTopics.value[i].id).length) return true
  }
  return false
})

// Navigation actions
const nextQuestion = () => {
  const currentQs = getQuestionsByTopic(selectedQuestion.value.topic_id)
  const idx = currentQs.findIndex(q => q.id === selectedQuestion.value.id)
  if (idx < currentQs.length - 1) {
    selectQuestion(currentQs[idx + 1])
  } else {
    const topicIdx = orderedTopics.value.findIndex(t => t.id === selectedQuestion.value.topic_id)
    for (let i = topicIdx + 1; i < orderedTopics.value.length; i++) {
      const nextQs = getQuestionsByTopic(orderedTopics.value[i].id)
      if (nextQs.length) {
        openChapters.value = [orderedTopics.value[i].chapter_id]
        openTopics.value = [orderedTopics.value[i].id]
        selectQuestion(nextQs[0])
        break
      }
    }
  }
}

const prevQuestion = () => {
  const currentQs = getQuestionsByTopic(selectedQuestion.value.topic_id)
  const idx = currentQs.findIndex(q => q.id === selectedQuestion.value.id)
  if (idx > 0) {
    selectQuestion(currentQs[idx - 1])
  } else {
    const topicIdx = orderedTopics.value.findIndex(t => t.id === selectedQuestion.value.topic_id)
    for (let i = topicIdx - 1; i >= 0; i--) {
      const prevQs = getQuestionsByTopic(orderedTopics.value[i].id)
      if (prevQs.length) {
        openChapters.value = [orderedTopics.value[i].chapter_id]
        openTopics.value = [orderedTopics.value[i].id]
        selectQuestion(prevQs[prevQs.length - 1])
        break
      }
    }
  }
}
   
const resetQuestion = () => {
   selectedAnswer.value = null
   selectedAnswers.value = []
   userAnswers.value = []
   correctAnswers.value = []
   resultStatus.value = null
   resultMessage.value = ''
}

function toggleSidebar() {
  showSidebar.value = !showSidebar.value
}

const toggleExplanation = () => {
  showExplanation.value = !showExplanation.value
}

onMounted(loadData)
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@100;400;500;700&display=swap');

.app {
  display: flex;
  flex-direction: column;
  height: 100vh;
  font-family: 'Inter', sans-serif;
}

.app__body {
  position: relative;
  display: flex;
  flex: 1;
  overflow: visible;
  background-color: #fff;
}

.sidebar--hidden {
  visibility: hidden;
}

.sidebar-toggle {
  position: absolute;
  left: 260px;               /* ровно ширина sidebar */
  top: 50%;
  transform: translateY(-50%);
  width: 28px;
  height: 28px;
  border-radius: 14px;
  background: #fff;
  border: 1px solid #ddd;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 10;
  padding: 0;
}

/* чуть больше «защиты» от клика по невидимому сайдбару */
.sidebar--hidden .sidebar__chapter,
.sidebar--hidden .sidebar__topic,
.sidebar--hidden .sidebar__question-btn {
  pointer-events: none;
}

.sidebar-toggle--visible {
   left: 18.5rem;
 }

 /* скрытая (sidebar скрыт) */
.sidebar-toggle--hidden {
  left: 1rem;
 }

.sidebar-toggle {
  width: 3rem;
  height: 3rem;
  border-radius: 1.5rem;
  top: 3.5rem;
}

 .sidebar-toggle svg {
   width: 24px;
   height: 24px;
 }

.sidebar {
  width: 17rem;
  background-color: #e6f8fc;
  padding: 24px;
  overflow-y: auto;
}

.main {
  flex: 1;
  padding: 32px;
  overflow: auto;
  position: relative;
  z-index: 1;
}

/* --- Sidebar --- */
.sidebar__chapter + .sidebar__chapter {
  margin-top: 16px;
}
.sidebar__chapter-title {
  font-size: 18px;
  font-weight: 700;
  cursor: pointer;
}
.sidebar__chapter-title:hover {
  color: #3182ce;
}
.sidebar__topics {
  margin-top: 8px;
  padding-left: 12px;
}
.sidebar__topic + .sidebar__topic {
  margin-top: 12px;
}
.sidebar__topic-title {
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
}
.sidebar__topic-title:hover {
  color: #4299e1;
}
.sidebar__questions {
  margin-top: 4px;
  padding-left: 16px;
  list-style-type: disc;
}
.sidebar__question {
  margin-bottom: 6px;
}
.sidebar__question-btn {
  background: none;
  border: none;
  padding: 0;
  font-size: 14px;
  cursor: pointer;
  text-align: left;
}
.sidebar__question-btn:hover {
  text-decoration: underline;
}

/* --- Question Panel --- */
.question {
  position: fixed;
  top: 4.5rem;
  left: 50%;             /* центрируем по горизонтали */
  transform: translateX(-50%);
  width: 20vw;
}
.question__title {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 24px;
}
.question__answers {
  list-style: none;
  padding: 0;
  margin: 0;
}
.question__answer {
  display: flex;
  align-items: center;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 12px;
  background-color: #fff;
  border: 1px solid #ddd;
}
.question__answer--correct {
  background-color: #e6fffa;
  border-color: #81e6d9;
}
.question__answer--wrong {
  background-color: #ffe6e6;
  border-color: #fc8181;
}
.question__label {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
}
.question__input {
  transform: scale(1.2);
}

/* --- Actions & Navigation --- */
.question__actions {
  margin-top: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: flex-start;
}
.btn {
  padding: 10px 20px;
  font-size: 14px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
}
.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.btn--submit {
  width: 50%;
  align-self: flex-start;
  background-color: #38a169;
  color: #fff;
}
.btn--submit:hover:not(:disabled) {
  background-color: #2f855a;
}
.btn--reset {
  width: 50%;
  align-self: flex-start;
  background-color: #fff;
  color: #2d3748;
  box-shadow: inset 0 0 0 2px #ccc;
  box-sizing: border-box;
  color: #8b8b8b;
}
.btn--reset:hover {
  background-color: #f7f7f7;
}

.question__result {
  font-size: 16px;
  font-weight: 600;
}
.question__result--correct {
  color: #2f855a;
}
.question__result--wrong {
  color: #c53030;
}

.question__nav {
  margin-top: 32px;
  display: flex;
  justify-content: space-between;
}
.btn--nav {
  background-color: #e6f8fc;
  color: #2d3748;
}
.btn--nav:hover:not(:disabled) {
  background-color: #c4dee4;
}

.main__placeholder {
  font-size: 16px;
  color: #718096;
}
.question__empty {
  color: #718096;
  font-size: 14px;
}

.btn--show-answer{
  display:flex;                 /* было inline-flex */
  align-items:center;
  gap:8px;                      /* расстояние между svg и текстом */

  width:50%;                    /* такая же ширина, как у .btn--submit */
  padding:0px 0px;            /* такие же внутренние отступы */
  margin-top: 0.5rem;                     /* убираем все внешние отступы */
  margin-bottom: -0.7rem;

  background:none;
  border:none;
  cursor:pointer;
  font-size:14px;
  color:#2d3748;
  text-align:left;              /* текст и иконка прижаты влево */
}

.question__explanation {
  margin-top: 16px;
  padding: 12px;
  background-color: #f7fbfd;
  border-radius: 8px;
  border: 1px solid #c4dee4;
  font-size: 14px;
  line-height: 1.5;
}
</style>