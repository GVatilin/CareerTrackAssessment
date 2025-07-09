<template>
  <div class="app">
    <invalidUserPanel v-show="user.username == 'Guest'"/>
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
      <aside :class="['sidebar', { 'sidebar--hidden': !showSidebar }]">
        <ul class="sidebar__list">
          <li v-for="chapter in chapters" :key="chapter.id">
            <button
              @click="toggleChapter(chapter.id)"
              :class="[
                'sidebar__chapter-title',
                { 'is-open': isChapterOpen(chapter.id) }
              ]"
            >
              {{ chapter.name }}
            </button>
            <ul v-if="isChapterOpen(chapter.id)" class="sidebar__list sidebar__list--nested">
              <li v-for="topic in getTopicsByChapter(chapter.id)" :key="topic.id">
                <button
                  @click="toggleTopic(topic.id)"
                  :class="[
                    'sidebar__topic-title',
                    { 'is-open': isTopicOpen(topic.id) }
                  ]"
                >
                  {{ topic.name }}
                </button>
                <ul
                  v-if="isTopicOpen(topic.id)"
                  class="sidebar__list sidebar__list--nested sidebar__list--nested-2"
                >
                  <li
                    v-for="question in getQuestionsByTopic(topic.id)"
                    :key="question.id"
                  >
                    <button
                      @click="selectQuestion(question)"
                      :class="[
                        'sidebar__question-title',
                        { 'is-active': selectedQuestion && selectedQuestion.id === question.id }
                      ]"
                    >
                      {{ question.description }}
                    </button>
                  </li>
                </ul>
              </li>
            </ul>
          </li>
        </ul>
      </aside>

      <!-- Main content -->
      <main class="main">
        <div v-if="selectedQuestion" class="question">
          <h2 class="question__title">
            {{ selectedQuestion.description }}
          </h2>

          <ul v-if="isSimple(selectedQuestion)" class="question__answers">
            <li v-for="answer in answers" :key="answer.id"
              :class="[
                'question__answer',
                resultStatus !== null && correctAnswers.includes(answer.id) && 'question__answer--correct',
                resultStatus !== null && userAnswers.includes(answer.id) && !correctAnswers.includes(answer.id) && 'question__answer--wrong'
              ]">
              <label class="question__label">
                <input v-if="selectedQuestion.type === 0"
                       type="radio"
                       :value="answer.id"
                       v-model="selectedAnswer"
                       :disabled="resultStatus !== null"
                       class="question__input" />
                <input v-else
                       type="checkbox"
                       :value="answer.id"
                       v-model="selectedAnswers"
                       :disabled="resultStatus !== null"
                       class="question__input" />
                <span>{{ answer.text }}</span>
              </label>
            </li>
          </ul>

          <!-- AI text questions -->
          <div v-else-if="isAI(selectedQuestion)" class="question__ai">
            <textarea v-model="aiResponse"
                      placeholder="Введите ваш ответ"
                      :disabled="resultStatus !== null"
                      class="ai-textarea"
                      :class="{
                     'ai-textarea--correct': aiScore === 2,
                     'ai-textarea--partial': aiScore === 1,
                     'ai-textarea--wrong'  : aiScore === 0
                    }"></textarea>
          </div>

          <!-- результат + feedback -->
          <div v-if="selectedQuestion && isAI(selectedQuestion) && resultStatus !== null"
                class="ai-result">
            <p :class="[
                'ai-result__msg',
                aiScore === 2 ? 'ai-result__msg--correct'
                : aiScore === 1 ? 'ai-result__msg--partial'
                : 'ai-result__msg--wrong'
              ]">
            {{ resultMessage }}
            </p>
            <div
              class="ai-result__feedback"
              v-html="aiFeedback"
            />
          </div>

          <div class="question__actions">
            <div class="submit-group">
              <button
                @click="resultStatus === null ? submitAnswers() : resetQuestion()"
                :class="['btn', resultStatus === null ? 'btn--submit' : 'btn--reset']"
                :disabled="resultStatus === null
                  ? (selectedQuestion.type === 0 && !selectedAnswer) ||
                    (selectedQuestion.type === 1 && !selectedAnswers.length) ||
                    (selectedQuestion.type === 2 && (!aiResponse.trim() || isAnalyzing))
                  : false"
              >
                {{ resultStatus === null ? 'Ответить' : 'Ответить ещё раз' }}
              </button>
              <p v-if="isAnalyzing" class="analyzing-text">Анализируем ответ...</p>
            </div>

            <button
              class="btn btn--show-answer"
              @click="toggleExplanation"
            >
              <svg width="16" height="16" viewBox="0 0 24 24">
                <line x1="4" y1="8" x2="12" y2="16" stroke="#333" stroke-width="2" />
                <line x1="20" y1="8" x2="12" y2="16" stroke="#333" stroke-width="2" />
              </svg>
              <span>{{ showExplanation ? 'Скрыть объяснение' : 'Показать объяснение' }}</span>
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
import invalidUserPanel from "../../components/NotRegistered.vue"

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
const aiResponse   = ref('')
const aiScore     = ref(null)   // 0 | 1 | 2
const aiFeedback  = ref('')     // текст от сервера
const isAnalyzing = ref(false)


const getToken = () => {
  const token = localStorage.getItem('chronoJWTToken')
  if (!token) throw new Error('Token is missing. Please log in.')
  return token
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
    `http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/question/get_questions/simple`,
  )
const fetchAIQuestions = () =>
  axios.get(
    `http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/question/get_questions/ai`,
  )


const fetchAnswers = async questionId => {
  try {
    const token = getToken()
    console.log('JWT token is', token)
    const { data } = await axios.get(
      `http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/question/get_answers_to_question/${questionId}`,
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
    const [chapRes, topicRes, questionRes, aiQuestionRes] = await Promise.all([
      fetchChapters(),
      fetchTopics(),
      fetchQuestions(),
      fetchAIQuestions(),
    ])

    chapters.value = chapRes.data
    topics.value = topicRes.data

    const sq = questionRes.data.map(q => ({ ...q, type: q.type }))
    const aq = aiQuestionRes.data.map(q => ({ ...q, type: 2 }))
    questions.value = [...sq, ...aq]

    await fetchUser()
  } catch (err) {
    console.error('Ошибка при загрузке данных:', err)
  }
}

const isSimple = q => q && (q.type === 0 || q.type === 1)
const isAI     = q => q && q.type === 2

const getTopicsByChapter = chapterId =>
  topics.value.filter(t => t.chapter_id === chapterId)

const getQuestionsByTopic = topicId =>
  questions.value.filter(q => q.topic_id === topicId)


const toggleChapter = id => {
  const idx = openChapters.value.indexOf(id)
  idx > -1 ? openChapters.value.splice(idx, 1) : openChapters.value.push(id)
  localStorage.setItem('openChapters', JSON.stringify(openChapters.value));
}
const isChapterOpen = id => openChapters.value.includes(id)

const toggleTopic = id => {
  const idx = openTopics.value.indexOf(id)
  idx > -1 ? openTopics.value.splice(idx, 1) : openTopics.value.push(id)
  localStorage.setItem('openTopics', JSON.stringify(openTopics.value));
}
const isTopicOpen = id => openTopics.value.includes(id)


const selectQuestion = async question => {
  resetQuestion()
  selectedQuestion.value = question
  selectedAnswer.value = null
  showExplanation.value = false
  aiResponse.value = ''
  localStorage.setItem('lastQuestion', question.id);

  await fetchAnswers(question.id)
  await loadState(question.id)
}

const submitAnswers = async () => {
  const token = getToken()

  try {
    let data

    if (selectedQuestion.value.type === 2) {
      /* AI-вопрос */
      isAnalyzing.value = true
      const res = await axios.post(
        `http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/question/check_ai_question`,
        {
          question_id: selectedQuestion.value.id,
          text: aiResponse.value.trim()
        },
        { headers: { Authorization: `Bearer ${token}` } }
      )

      aiScore.value    = res.data.score
      aiFeedback.value = res.data.feedback
      resultStatus.value  = true
      resultMessage.value = aiScore.value === 2 ? 'Правильно!'
                          : aiScore.value === 1 ? 'Частичный ответ'
                                                : 'Неправильно'
    } else {
      /* Обычный (radio | checkbox) */
      userAnswers.value =
        selectedQuestion.value.type === 0
         ? [selectedAnswer.value]
          : [...selectedAnswers.value]

      const res = await axios.post(
        `http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/question/check_user_answers`,
        {
          question_id: selectedQuestion.value.id,
          selected_answer_id: userAnswers.value
        },
        { headers: { Authorization: `Bearer ${token}` } }
      )
      data = res.data
      correctAnswers.value = data.correct_answer_id ?? []
    }
    
    resultStatus.value = data.is_user_right
    resultMessage.value = data.is_user_right ? 'Правильно!' : 'Неправильно'

    saveState()
  } catch (err) {
    console.error('Ошибка при проверке ответов:', err)
  } finally {
    isAnalyzing.value = false
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
    selectedAnswer.value   = null;
    selectedAnswers.value  = [];
    aiResponse.value       = '';
    userAnswers.value      = [];
    correctAnswers.value   = [];
    resultStatus.value     = null;
    resultMessage.value    = '';
    aiScore.value          = null;
    aiFeedback.value       = '';
    showExplanation.value  = false;

    if (selectedQuestion.value?.id) {
      localStorage.removeItem(`question_state_${selectedQuestion.value.id}`);
    }
}

function toggleSidebar() {
  showSidebar.value = !showSidebar.value
}

const toggleExplanation = () => {
  showExplanation.value = !showExplanation.value
}

function saveState() {
  if (!selectedQuestion.value) return;
  const key = `question_state_${selectedQuestion.value.id}`;
  const state = {
    selectedAnswer: selectedAnswer.value,
    selectedAnswers: selectedAnswers.value,
    aiResponse: aiResponse.value,
    resultStatus: resultStatus.value,
    resultMessage: resultMessage.value,
    userAnswers: userAnswers.value,
    correctAnswers: correctAnswers.value,
    aiScore: aiScore.value,
    aiFeedback: aiFeedback.value
  };
  localStorage.setItem(key, JSON.stringify(state));
}

// Загрузить сохранённое состояние вопроса
async function loadState(questionId) {
  const key = `question_state_${questionId}`;
  const json = localStorage.getItem(key);
  if (!json) return;
  const s = JSON.parse(json);
  selectedAnswer.value  = s.selectedAnswer;
  selectedAnswers.value = s.selectedAnswers;
  aiResponse.value      = s.aiResponse;
  resultStatus.value    = s.resultStatus;
  resultMessage.value   = s.resultMessage;
  userAnswers.value     = s.userAnswers;
  correctAnswers.value  = s.correctAnswers;
  aiScore.value         = s.aiScore;
  aiFeedback.value      = s.aiFeedback;
}

 onMounted(async () => {
   const savedCh = localStorage.getItem('openChapters')
   if (savedCh) openChapters.value = JSON.parse(savedCh)
   const savedTp = localStorage.getItem('openTopics')
   if (savedTp) openTopics.value   = JSON.parse(savedTp)

   await loadData()

  // восстановить последний выбранный вопрос
   const last = localStorage.getItem('lastQuestion')
   if (last) {
     const q = questions.value.find(x => x.id === last)
     if (q) await selectQuestion(q)
   }
 })

</script>

<style scoped>
.app {
  display: flex;
  flex-direction: column;
  height: 100vh;
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
.sidebar__chapter-title {
  font-size: 18px;
  font-weight: 700;
  cursor: pointer;
  margin-top: 0rem;
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
  top: 4rem;
  left: 50%;             /* центрируем по горизонтали */
  transform: translateX(-50%);
  width: 25vw;
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
  margin-top: -0.7rem;
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

.ai-textarea {
  width: 100%;
  box-sizing: border-box;  /* ← вот это важно! */
  min-height: 120px;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 8px;
  resize: vertical;
  max-height: 60vh;
  overflow-y: auto;
}

/* рамка текстового поля */
.ai-textarea--correct { 
  border: 2px solid #81e6d9; 
  background-color: #e6fffa;
}
.ai-textarea--partial { 
  border: 2px solid #e49159; 
  background-color: #e6cab7;
}
.ai-textarea--wrong   { 
  border: 2px solid #fc8181; 
  background-color: #ffe6e6;
}

/* подпись под полем */
.ai-result__msg--correct { color: #81e6d9; }
.ai-result__msg--partial { color: #e49159; }
.ai-result__msg--wrong   { color: #fc8181; }

.ai-result__feedback {
  margin-top: 4px;
  font-size: 14px;
  color: #4a5568;
}

.submit-group {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%; 
}

.analyzing-text {
  color: #9b9b9b; 
  margin: 0;
  margin-left: 0.5rem;
  font-size: 1rem;
}

.sidebar__list {
  list-style: none;
  margin: 0;
  padding: 0;
}

/* общий стиль для всех кнопок-элементов */
.sidebar__chapter-title,
.sidebar__topic-title,
.sidebar__question-title {
  display: flex;
  align-items: center;
  background: none;
  border: none;
  padding: 4px 0;
  cursor: pointer;
  text-align: left;
}

.sidebar__chapter-title {
  font-size: 1.3rem;
}

.sidebar__topic-title {
  font-size: 1rem;
}

.sidebar__question-title {
  font-size: 0.9rem;
}

/* Глава: ➔ */
.sidebar__chapter-title::before {
  content: '➙';
  display: inline-block;
  width: 1em;
  transition: transform 0.2s;
  margin-right: 0.5em;
}
.sidebar__chapter-title.is-open::before {
  transform: rotate(45deg);
}

/* Топик: ➙ */
.sidebar__list--nested .sidebar__topic-title {
  margin-left: 1em;
}
.sidebar__topic-title::before {
  content: '➙';
  display: inline-block;
  width: 1em;
  transition: transform 0.2s;
  margin-right: 0.5em;
}
.sidebar__topic-title.is-open::before {
  transform: rotate(45deg);
}

/* Вопрос: ? */
.sidebar__list--nested-2 .sidebar__question-title {
  margin-left: 0 !important;
  padding-left: 2px;
  color: #333;
}
.sidebar__question-title::before {
  content: '?';
  display: inline-block;
  width: 1em;
  color: #38a169; /* зелёный, как в скрине */
}
.sidebar__question-title.is-active {
  color: #2f855a;
  font-weight: 500;
}
.sidebar__question-title.is-active::before {
  color: #2f855a;
}

.sidebar__list--nested-2 {
  padding-left: 2em;     /* сдвигает вправо и стрелку, и сам текст вопросов */
}
.sidebar__chapter-title::before,
.sidebar__topic-title::before,
.sidebar__question-title::before {
  display: inline-block;
  width: 1em;         /* иконка занимает 1em */
  margin-right: 0.3em;/* одинаковый отступ до текста */
  transition: transform 0.2s;
}

</style>