<template>
  <div class="flex h-screen">
    <!-- Sidebar -->
    <aside class="w-1/4 bg-gray-100 p-4 overflow-y-auto">
      <div v-for="chapter in chapters" :key="chapter.id" class="mb-4">
        <h2 @click="toggleChapter(chapter.id)" class="font-bold cursor-pointer hover:text-blue-600">
          {{ chapter.name }}
        </h2>
        <div v-if="isChapterOpen(chapter.id)" class="ml-4 mt-2">
          <div v-for="topic in getTopicsByChapter(chapter.id)" :key="topic.id" class="mb-2">
            <h3 @click="toggleTopic(topic.id)" class="font-semibold cursor-pointer hover:text-blue-500">
              {{ topic.name }}
            </h3>
            <ul v-if="isTopicOpen(topic.id)" class="ml-4 mt-1 list-disc">
              <li v-for="question in getQuestionsByTopic(topic.id)" :key="question.id">
                <button @click="selectQuestion(question)" class="text-left hover:underline">
                  {{ question.description }}
                </button>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </aside>

    <!-- Main content -->
    <main class="flex-1 p-8">
      <div v-if="selectedQuestion">
        <h2 class="text-2xl font-bold mb-4">
          {{ selectedQuestion.description }}
        </h2>

        <!-- Answers -->
        <ul v-if="answers.length" class="space-y-2">
          <li
            v-for="answer in answers"
            :key="answer.id"
            :class="{
              'bg-green-100': correctAnswers?.includes(answer.id),
              'bg-red-100': userAnswers?.includes(answer.id) && !correctAnswers?.includes(answer.id)
            }"
            class="p-2 rounded"
          >
            <label class="inline-flex items-center space-x-2">
              <!-- Single vs Multiple choice -->
              <input
                v-if="selectedQuestion.type === 0"
                type="radio"
                :value="answer.id"
                v-model="selectedAnswer"
                class="form-radio"
                :disabled="resultStatus !== null"
              />
              <input
                v-else
                type="checkbox"
                :value="answer.id"
                v-model="selectedAnswers"
                class="form-checkbox"
                :disabled="resultStatus !== null"
              />
              <span>{{ answer.text }}</span>
            </label>
          </li>
        </ul>
        <div v-else class="text-gray-500">Ответы не найдены.</div>

        <!-- Submit Button -->
        <button
          @click="submitAnswers"
          class="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          :disabled="resultStatus !== null ||
                     (selectedQuestion.type === 0 && !selectedAnswer) ||
                     (selectedQuestion.type !== 0 && !selectedAnswers.length)"
        >
          Ответить
        </button>

        <!-- Result Message -->
        <p v-if="resultStatus !== null" class="mt-4 text-lg font-semibold"
           :class="resultStatus ? 'text-green-600' : 'text-red-600'">
          {{ resultMessage }}
        </p>
      </div>

      <div v-else class="text-gray-500">
        <p>Выберите вопрос слева, чтобы начать тест.</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'


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
    correctAnswers.value = data.correct_answer_ids
  } catch (err) {
    console.error('Ошибка при проверке ответов:', err)
  }
}


onMounted(loadData)
</script>

<style scoped>
.flex {
  display: flex;
}
.h-screen {
  height: 100vh;
}
.w-1\/4 {
  width: 25%;
}
.bg-gray-100 {
  background-color: #f7fafc;
}
.p-4 {
  padding: 1rem;
}
.p-8 {
  padding: 2rem;
}
.overflow-y-auto {
  overflow-y: auto;
}
.cursor-pointer {
  cursor: pointer;
}
.font-bold {
  font-weight: 700;
}
.font-semibold {
  font-weight: 600;
}
.hover\:text-blue-600:hover {
  color: #3182ce;
}
.hover\:text-blue-500:hover {
  color: #4299e1;
}
.hover\:underline:hover {
  text-decoration: underline;
}
</style>
