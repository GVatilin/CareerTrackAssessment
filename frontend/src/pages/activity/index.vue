<template>
  <div class="question-page">
    <invalidUserPanel v-show="user.username == 'Guest'" />
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

        <!-- QUESTION CREATION MODE -->
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

          <!-- IMAGE UPLOAD BLOCK -->
          <div class="question-card__field">
            <label for="qImage">Изображение к вопросу:</label>
            <input id="qImage" type="file" accept="image/*" @change="handleImage" />
            <img v-if="imagePreview" :src="imagePreview" class="image-preview" />
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
                <button v-if="answers.length > 2" type="button" class="remove-btn" @click="removeAnswer(idx)">×</button>
              </div>
            </div>
            <button type="button" class="btn-add" @click="addAnswer">Добавить вариант</button>
          </template>
        </template>

        <!-- CHAPTER CREATION MODE -->
        <div v-if="creationMode === 'chapter'" class="question-card__field">
          <label for="chapterName">Название раздела:</label>
          <input id="chapterName" v-model="chapterName" class="large-input" placeholder="Введите название раздела" />
        </div>

        <!-- TOPIC CREATION MODE -->
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

        <button class="btn-submit" type="submit" :disabled="isSubmitDisabled">Создать</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import NavBar from '@/components/NavBar.vue'
import invalidUserPanel from "../../components/NotRegistered.vue"

// ---------- STATE ---------- //
const chapters            = ref([])
const topics              = ref([])
const user                = ref({ username: 'Loading...' })

const creationMode        = ref('question')
const questionChapterId   = ref('')
const questionTopicId     = ref('')
const questionType        = ref('open')
const questionText        = ref('')
const criteria            = ref('')
const answers             = ref([{ text: '' }, { text: '' }])
const correctIndices      = ref([])
const chapterName         = ref('')
const topicName           = ref('')
const selectedChapterId   = ref('')

// image upload
const imageFile     = ref(null)
const imagePreview  = ref(null)

// ---------- API HELPERS ---------- //
const getToken = () => {
  const token = localStorage.getItem('chronoJWTToken')
  if (!token) throw new Error('JWT token not found')
  return token
}

const base = `http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1`

const fetchAll = async () => {
  const headers = { Authorization: `Bearer ${getToken()}` }
  const [chap, top] = await Promise.all([
    axios.get(`${base}/topic/get_chapters`, { headers }),
    axios.get(`${base}/topic/get_topics`,   { headers })
  ])
  chapters.value = chap.data
  topics.value   = top.data
}

const fetchUser = async () => {
  try {
    const { data } = await axios.get(`${base}/user/me`, {
      headers: { Authorization: `Bearer ${getToken()}` }
    })
    user.value = data
  } catch {
    user.value.username = 'Guest'
  }
}

onMounted(async () => {
  await fetchUser()
  if (user.value.username !== 'Guest') await fetchAll()
})

// ---------- COMPUTEDS ---------- //
const topicsForQuestion = computed(() => topics.value.filter(t => t.chapter_id === questionChapterId.value))

const isSubmitDisabled = computed(() => {
  /* ── создание раздела ─────────────────────────────── */
  if (creationMode.value === 'chapter') {
    return !chapterName.value.trim()
  }

  /* ── создание темы ────────────────────────────────── */
  if (creationMode.value === 'topic') {
    return !topicName.value.trim() || !selectedChapterId.value
  }

  /* ── создание вопроса ─────────────────────────────── */
  if (!questionChapterId.value || !questionTopicId.value || !questionText.value.trim()) {
    return true
  }

  /* ● ОТКРЫТЫЙ ОТВЕТ */
  if (questionType.value === 'open') {
    return !criteria.value.trim()           // только критерии
  }

  /* ● ВЫБОР ОТВЕТА */
  if (answers.value.length < 2) return true
  if (answers.value.some(a => !a.text.trim())) return true
  if (correctIndices.value.length === 0) return true

  return false                              // всё ок
})

// ---------- METHODS ---------- //
const addAnswer = () => answers.value.push({ text: '' })
const removeAnswer = idx => {
  answers.value.splice(idx, 1)
  correctIndices.value = correctIndices.value
    .filter(i => i !== idx)
    .map(i => (i > idx ? i - 1 : i))
}

const handleImage = e => {
  const file = e.target.files[0]
  if (!file) return
  imageFile.value    = file
  imagePreview.value = URL.createObjectURL(file)
}

const resetForm = () => {
  questionChapterId.value = questionTopicId.value = ''
  questionType.value      = 'open'
  questionText.value      = criteria.value = ''
  answers.value           = [{ text: '' }, { text: '' }]
  correctIndices.value    = []
  chapterName.value       = topicName.value = selectedChapterId.value = ''
  imageFile.value         = null
  imagePreview.value      = null
}

const uploadImage = async (questionId, token) => {
  console.log('uploadImage', { id: questionId, file: imageFile.value });

  if (!imageFile.value) return;          // файл не выбран — выходим

  const fd = new FormData();
  fd.append('file', imageFile.value, imageFile.value.name);

  try {
    await axios.post(
      `${base}/file/questions/${questionId}/upload`, // ← ровно такой URL
      fd,
      {
        headers: { Authorization: `Bearer ${token}` }, // Content-Type ставит Axios
        onUploadProgress: e => {
          console.log(`Upload ${Math.round((e.loaded / e.total) * 100)}%`);
        },
      },
    );
  } catch (err) {
    console.error('Ошибка загрузки изображения:', err.response?.data || err);
  }
};

const onSubmit = async () => {
  const token   = getToken()
  const headers = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }

  try {
    if (creationMode.value === 'question') {
      let createResp
      if (questionType.value === 'open') {
        createResp = await axios.post(
          `${base}/question/create_ai_question`,
          {
            description: questionText.value,
            topic_id: questionTopicId.value,
            explanation: criteria.value
          },
          { headers }
        )
      } else {
        createResp = await axios.post(
          `${base}/question/create_question`,
          {
            question: {
              description: questionText.value,
              type: correctIndices.value.length > 1 ? 2 : 1,
              topic_id: questionTopicId.value,
              explanation: ''
            },
            answers: answers.value.map((a, i) => ({ text: a.text, is_correct: correctIndices.value.includes(i) }))
          },
          { headers }
        )
      }

      console.log('CREATE_RESPONSE', createResp.data);
      const questionId = createResp.data.id
      if (!questionId) {
        console.warn('Не удалось получить ID вопроса из ответа', createResp.data)
      }

      if (questionId) {
        await uploadImage(questionId, token)
      }

    } else if (creationMode.value === 'chapter') {
      await axios.post(
        `${base}/topic/create_chapter`,
        { name: chapterName.value },
        { headers }
      )
    } else {
      await axios.post(
        `${base}/topic/create_topic`,
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
  background-color: #ffffff;
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
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  width: 35%;
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
  border: 1px solid #87b4dd;
  border-radius: 6px;
}
.question-card__field textarea {
  min-height: 140px;
  resize: vertical;
}

.image-preview {
  margin-top: 0.5rem;
  max-width: 150px;
  max-height: 150px;
  object-fit: contain;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
}

.btn-submit {
  font-size: 1.1rem;
  font-weight: 600;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  background-color: #38a169;
  color: #fff;
  align-self: center;
  transition: background-color 0.3s;
  width: 25%;
  height: 3rem;
}

.btn-submit:hover {
  background-color: #2f855a;
}

.btn-add {
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  align-self: flex-start;
  background-color: #87b4dd;
  color: #fff;
  border-radius: 6px;
  border: 0;
}

.btn-add:hover {
  background-color: #7a9cbd;
}
</style>