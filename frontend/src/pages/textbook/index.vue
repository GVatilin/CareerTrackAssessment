<template>
  <div class="app">
    <NavBar :username="user.username" />

    <div class="app__body">
      <!-- Sidebar -->
      <aside class="sidebar">
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
              @click="submitAnswers"
              class="btn btn--submit"
              :disabled="
                resultStatus !== null ||
                (selectedQuestion.type === 0 && !selectedAnswer) ||
                (selectedQuestion.type !== 0 && !selectedAnswers.length)
              "
            >
              Ответить
            </button>

            <p
              v-if="resultStatus !== null"
              class="question__result"
              :class="resultStatus ? 'question__result--correct' : 'question__result--wrong'"
            >
              {{ resultMessage }}
            </p>

            <button
              v-if="resultStatus !== null"
              @click="resetQuestion"
              class="btn btn--reset"
            >
              Ответить ещё раз
            </button>
          </div>

          <div class="question__nav">
            <button
              @click="prevQuestion"
              :disabled="!hasPrev"
              class="btn btn--nav"
            >
              Prev
            </button>
            <button
              @click="nextQuestion"
              :disabled="!hasNext"
              class="btn btn--nav"
            >
              Next
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
  display: flex;
  flex: 1;
  overflow: hidden;
}
.sidebar {
  width: 260px;
  background-color: #f0f8fa;
  padding: 24px;
  overflow-y: auto;
}
.main {
  flex: 1;
  padding: 32px;
  overflow-y: auto;
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
  max-width: 600px;
  margin: 0 auto;
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
}
.btn {
  padding: 10px 20px;
  font-size: 14px;
  border-radius: 12px;
  border: none;
  cursor: pointer;
}
.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.btn--submit {
  background-color: #3182ce;
  color: #fff;
}
.btn--submit:hover:not(:disabled) {
  background-color: #2b6cb0;
}
.btn--reset {
  background-color: #edf2f7;
  color: #2d3748;
}
.btn--reset:hover {
  background-color: #e2e8f0;
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
  background-color: #edf2f7;
  color: #2d3748;
}
.btn--nav:hover:not(:disabled) {
  background-color: #e2e8f0;
}

.main__placeholder {
  font-size: 16px;
  color: #718096;
}
.question__empty {
  color: #718096;
  font-size: 14px;
}

</style>