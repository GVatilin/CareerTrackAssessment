<template>
  <div class="profile-page">
    <invalidUserPanel v-show="user.username == 'Guest'"/>
    <NavBar :username="user.username" />

    <div class="profile-page__content">
      <div class="profile-card">
        <div class="profile-card__info">
          <h2 class="profile-card__username">{{ user.username }}</h2>
        </div>

        <div
          class="profile-card__avatar-container"
          @mouseenter="hover = true"
          @mouseleave="hover = false"
        >
          <img
            :src="avatarUrl"
            alt="User Avatar"
            class="profile-card__avatar-image"
            @click="triggerFileInput"
          />
          <input
            type="file"
            ref="fileInput"
            style="display: none"
            @change="handleFileChange"
          />
          <div v-if="hover" class="overlay" @click="triggerFileInput">
            <span class="change-text">Изменить аватарку</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showCropper" class="cropper-modal">
      <div class="cropper-container">
        <img ref="cropperImage" :src="selectedImageUrl" alt="Selected Image" />
        <div class="cropper-controls">
          <label>
            Ширина:
            <input v-model.number="cropWidth" type="number" min="50" />
          </label>
          <label>
            Высота:
            <input v-model.number="cropHeight" type="number" min="50" />
          </label>
        </div>
        <button @click="cropImage">Обрезать и сохранить</button>
        <button @click="cancelCrop">Отмена</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import axios from 'axios'
import Cropper from 'cropperjs'
import 'cropperjs/dist/cropper.css'
import NavBar from '../../components/NavBar.vue'


const user = ref({
  username: 'Loading...',
  status: ''
})

const avatarUrl = ref(null)
const hover = ref(false)
const fileInput = ref(null)
const showCropper = ref(false)
const selectedImageUrl = ref('')
const cropperInstance = ref(null)
const cropperImage = ref(null)
const cropWidth = ref(190)
const cropHeight = ref(190)


const getToken = () => {
  const token = localStorage.getItem('chronoJWTToken')
  if (!token) throw new Error('Token is missing. Please log in.')
  return token
}

const fetchUser = async () => {
  try {
    const token = getToken()
    const { data } = await axios.get(
      `http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/user/me`,
      { headers: { Authorization: `Bearer ${token}` } }
    )
    user.value.username = data.username
    user.value.status = data.status || 'inactive'
  } catch (err) {
    console.error('Ошибка при загрузке профиля:', err)
  }
}

const fetchAvatar = async () => {
  try {
    const token = getToken()
    const response = await axios.get(
      `http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/file/get`,
      {
        headers: { Authorization: `Bearer ${token}` },
        responseType: 'blob'
      }
    )
    avatarUrl.value = URL.createObjectURL(response.data)
  } catch (err) {
    console.error('Error fetching avatar:', err)
    avatarUrl.value = null
  }
}

const triggerFileInput = () => {
  fileInput.value && fileInput.value.click()
}

const handleFileChange = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  selectedImageUrl.value = URL.createObjectURL(file)
  showCropper.value = true
  await nextTick()
  cropperInstance.value?.destroy()
  cropperInstance.value = new Cropper(cropperImage.value, {
    aspectRatio: 1,
    viewMode: 1
  })
}

const cropImage = () => {
  if (!cropperInstance.value) return
  const canvas = cropperInstance.value.getCroppedCanvas({
    width: cropWidth.value,
    height: cropHeight.value
  })
  canvas.toBlob(async (blob) => {
    if (!blob) return
    try {
      const token = getToken()
      const formData = new FormData()
      formData.append('file', new File([blob], 'avatar.jpg', { type: blob.type }))
      await axios.post(
        `http://${process.env.VUE_APP_BACKEND_URL}:8080/api/v1/file/upload`,
        formData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        }
      )
      await fetchAvatar()
    } catch (err) {
      console.error('Error uploading avatar:', err)
    } finally {
      cropperInstance.value.destroy()
      cropperInstance.value = null
      showCropper.value = false
      URL.revokeObjectURL(selectedImageUrl.value)
      selectedImageUrl.value = ''
    }
  }, 'image/jpeg')
}

const cancelCrop = () => {
  cropperInstance.value?.destroy()
  cropperInstance.value = null
  showCropper.value = false
  URL.revokeObjectURL(selectedImageUrl.value)
  selectedImageUrl.value = ''
}

onMounted(async () => {
  await fetchUser()
  await fetchAvatar()
})
</script>

<style scoped>
.profile-page__content {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
}

.profile-card {
  display: flex;
  flex-direction: row-reverse;
  align-items: flex-start;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  padding: 2rem;
  max-width: 600px;
  width: 100%;
  gap: 1.5rem;
}

.profile-card__info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.profile-card__username {
  font-size: 1.75rem;
  font-weight: 700;
  margin: 0 0 1rem;
}

.profile-card__status {
  font-weight: 500;
  margin: 0;
}

.profile-card__status span {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.profile-card__status .active {
  background-color: #e6fffa;
  color: #2c7a7b;
}

.profile-card__status .inactive {
  background-color: #ffe6e6;
  color: #c53030;
}

.profile-card__tests {
  font-weight: 500;
  margin-top: 0.5rem;
}

.profile-card__tests span {
  font-weight: 700;
}

.profile-card__avatar-container {
  position: relative;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  overflow: hidden;
  background-color: #f9f9f9;
  cursor: pointer;
}

.profile-card__avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.change-text {
  font-size: 1em;
  color: #fff;
  text-align: center;
}

.cropper-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.cropper-container {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
}

.cropper-controls {
  margin: 10px 0;
}

.cropper-controls label {
  margin: 0 10px;
  font-size: 0.9rem;
}

.cropper-controls input {
  padding: 5px;
  width: 60px;
}

.cropper-container button {
  padding: 8px 16px;
  margin: 8px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.cropper-container button:first-of-type {
  background-color: #2c7a7b;
  color: #fff;
}

.cropper-container button:last-of-type {
  background-color: #c53030;
  color: #fff;
}
</style>
