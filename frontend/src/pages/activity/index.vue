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
            <select id="qChapter" v-model="questionChapterId" @change="onQuestionChapterChange">
              <option disabled value="">-- выберите раздел --</option>
              <option v-for="chap in chapters" :key="chap.id" :value="chap.id">
                {{ chap.name }}
              </option>
            </select>
          </div>
          <div class="question-card__field" v-if="questionChapterId">
            <label for="qTopic">Тема:</label>
            <select id="qTopic" v-model="questionTopicId">
              <option disabled value="">-- выберите тему --</option>
              <option
                v-for="t in topicsForQuestion"
                :key="t.id"
                :value="t.id"
              >
                {{ t.name }}
              </option>
            </select>
          </div>
          <div class="question-card__field">
            <label for="questionType">Тип вопроса:</label>
            <select id="questionType" v-model="questionType">
              <option value="open">С открытым ответом</option>
              <option value="choice">С выбором ответа</option>
            </select>
          </div>

          <!-- Текст -->
          <div class="question-card__field">
            <label for="questionText">Текст вопроса:</label>
            <textarea
              id="questionText"
              v-model="questionText"
              class="large-field"
              placeholder="Введите текст вопроса"
            ></textarea>
          </div>
          <div v-if="questionType === 'open'" class="question-card__field">
            <label for="criteria">Пояснение / критерии:</label>
            <textarea
              id="criteria"
              v-model="criteria"
              class="large-field"
              placeholder="Введите пояснение или критерии ответа"
            ></textarea>
          </div>

          <div v-else class="question-card__field">
            <label for="correctAnswer">Правильный ответ:</label>
            <input
              id="correctAnswer"
              type="text"
              v-model="correctAnswer"
              class="large-input"
              placeholder="Введите правильный ответ"
            />
          </div>
        </template>
        <div v-if="creationMode === 'chapter'" class="question-card__field">
          <label for="chapterName">Название раздела:</label>
          <input
            id="chapterName"
            type="text"
            v-model="chapterName"
            class="large-input"
            placeholder="Введите название раздела"
          />
        </div>
        <template v-if="creationMode === 'topic'">
          <div class="question-card__field">
            <label for="topicName">Название темы:</label>
            <input
              id="topicName"
              type="text"
              v-model="topicName"
              class="large-input"
              placeholder="Введите название темы"
            />
          </div>
          <div class="question-card__field">
            <label for="selectedChapter">Выберите раздел:</label>
            <select id="selectedChapter" v-model="selectedChapterId" class="large-input">
              <option disabled value="">-- выберите раздел --</option>
              <option v-for="chap in chapters" :key="chap.id" :value="chap.id">
                {{ chap.name }}
              </option>
            </select>
          </div>
        </template>
        <button type="submit" class="btn" :disabled="isSubmitDisabled">
          Создать
        </button>
      </form>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, onMounted, computed } from 'vue'
import axios from 'axios'
import NavBar from '@/components/NavBar.vue'

export default defineComponent({
  name: 'QuestionPage',
  components: { NavBar },
  setup() {
    const user = ref({ username: 'Loading...' })
    const chapters = ref([])
    const topics = ref([])
    const creationMode = ref('question') 
    const questionChapterId = ref('')
    const questionTopicId = ref('')
    const questionType = ref('open')
    const questionText = ref('')
    const criteria = ref('')
    const correctAnswer = ref('')
    const chapterName = ref('')
    const topicName = ref('')
    const selectedChapterId = ref('') 

    const getToken = () => {
      const token = localStorage.getItem('chronoJWTToken')
      if (!token) throw new Error('Token missing')
      return token
    }

    const fetchUser = async () => {
      const token = getToken()
      const { data } = await axios.get(
        `http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/user/me`,
        { headers: { Authorization: `Bearer ${token}` } }
      )
      user.value.username = data.username
    }

    const fetchChapters = async () => {
      const token = getToken()
      const { data } = await axios.get(
        `http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/topic/get_chapters`,
        { headers: { Authorization: `Bearer ${token}` } }
      )
      chapters.value = data
    }

    const fetchTopics = async () => {
      const token = getToken()
      const { data } = await axios.get(
        `http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/topic/get_topics`,
        { headers: { Authorization: `Bearer ${token}` } }
      )
      topics.value = data
    }

    onMounted(async () => {
      try {
        await fetchUser()
        await Promise.all([fetchChapters(), fetchTopics()])
      } catch (e) {
        console.error(e)
      }
    })

    const topicsForQuestion = computed(() =>
      topics.value.filter(t => t.chapter_id === questionChapterId.value)
    )

    const onQuestionChapterChange = () => {
      questionTopicId.value = ''
    }

    const isSubmitDisabled = computed(() => {
      if (creationMode.value === 'chapter') {
        return !chapterName.value.trim()
      }
      if (creationMode.value === 'topic') {
        return !topicName.value.trim() || !selectedChapterId.value
      }
      if (!questionChapterId.value || !questionTopicId.value || !questionText.value.trim()) return true
      if (questionType.value === 'open') {
        return !criteria.value.trim()
      }
      return !correctAnswer.value.trim()
    })

    const createChapter = async () => {
      const token = getToken()
      await axios.post(
        `http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/topic/create_chapter`,
        { name: chapterName.value },
        { headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' } }
      )
    }

    const createTopic = async () => {
      const token = getToken()
      await axios.post(
        `http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/topic/create_topic`,
        { name: topicName.value, chapter_id: selectedChapterId.value },
        { headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' } }
      )
    }

    const createQuestion = async () => {
      const token = getToken()
      if (questionType.value === 'open') {
        await axios.post(
          `http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/question/create_ai_question`,
          {
            description: questionText.value,
            topic_id: questionTopicId.value,
            explanation: criteria.value
          },
          { headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' } }
        )
      } else {
        await axios.post(
          `http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/question/create_question`,
          {
            question: {
              description: questionText.value,
              type: 0,
              topic_id: questionTopicId.value,
              explanation: ''
            },
            answers: [ { text: correctAnswer.value, is_correct: true } ]
          },
          { headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' } }
        )
      }
    }

    // ---------------- submit handler
    const resetForm = () => {
      chapterName.value = ''
      topicName.value = ''
      selectedChapterId.value = ''
      questionChapterId.value = ''
      questionTopicId.value = ''
      questionText.value = ''
      criteria.value = ''
      correctAnswer.value = ''
      questionType.value = 'open'
    }

    const onSubmit = async () => {
      try {
        if (creationMode.value === 'chapter') {
          await createChapter()
        } else if (creationMode.value === 'topic') {
          await createTopic()
        } else {
          await createQuestion()
        }
        await Promise.all([fetchChapters(), fetchTopics()])
        resetForm()
      } catch (err) {
        console.error('Ошибка создания:', err)
      }
    }

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
      correctAnswer,
      chapterName,
      topicName,
      selectedChapterId,
      isSubmitDisabled,
      onQuestionChapterChange,
      onSubmit
    }
  }
})
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
  align-items: center;
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
