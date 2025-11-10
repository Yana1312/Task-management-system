import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import path from 'path'
import fs from 'fs'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

function avatarUploadBase64Plugin() {
  const avatarsDir = path.resolve(__dirname, './public/resources/avatars')
  fs.mkdirSync(avatarsDir, { recursive: true })

  return {
    name: 'avatar-upload-base64-middleware',
    configureServer(server) {
      server.middlewares.use('/api/upload-avatar-base64', async (req, res) => {
        try {
          const chunks = []
          for await (const chunk of req) chunks.push(chunk)
          const bodyStr = Buffer.concat(chunks).toString('utf8')
          let payload
          try {
            payload = JSON.parse(bodyStr || '{}')
          } catch (e) {
            res.statusCode = 400
            res.setHeader('Content-Type', 'application/json')
            res.end(JSON.stringify({ error: 'Invalid JSON body' }))
            return
          }

          const uid = String(payload?.uid || 'user')
          const data = String(payload?.data || '')
          const originalName = String(payload?.filename || 'avatar.jpg')

          if (!data) {
            res.statusCode = 400
            res.setHeader('Content-Type', 'application/json')
            res.end(JSON.stringify({ error: 'No data provided' }))
            return
          }

          const safeUid = uid.replace(/[^a-zA-Z0-9_-]/g, '') || 'user'
          const ext = (path.extname(originalName || '') || '.jpg').toLowerCase() || '.jpg'
          const base64 = data.includes(',') ? data.split(',')[1] : data
          const buffer = Buffer.from(base64, 'base64')

          const fileName = `${safeUid}_${Date.now()}${ext}`
          const filePath = path.join(avatarsDir, fileName)
          await fs.promises.writeFile(filePath, buffer)

          const url = `/resources/avatars/${fileName}`
          res.setHeader('Content-Type', 'application/json')
          res.end(JSON.stringify({ url }))
        } catch (e) {
          res.statusCode = 500
          res.setHeader('Content-Type', 'application/json')
          res.end(JSON.stringify({ error: 'Upload failed' }))
        }
      })
    }
  }
}

export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
    avatarUploadBase64Plugin(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
  },
})
