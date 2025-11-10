import express from 'express'
import multer from 'multer'
import path from 'path'
import fs from 'fs'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const app = express()
const PORT = process.env.PORT || 3001

app.use(express.json({ limit: '6mb' }))

const avatarsDir = path.resolve(__dirname, '../public/resources/avatars')
fs.mkdirSync(avatarsDir, { recursive: true })

const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, avatarsDir)
  },
  filename: (req, file, cb) => {
    const uid = (req.body?.uid || 'user')
    const ext = (path.extname(file.originalname || '') || '.jpg').toLowerCase()
    const safeUid = String(uid).replace(/[^a-zA-Z0-9_-]/g, '') || 'user'
    const name = `${safeUid}_${Date.now()}${ext || '.jpg'}`
    cb(null, name)
  }
})

const upload = multer({
  storage,
  limits: { fileSize: 5 * 1024 * 1024 },
})

app.post('/api/upload-avatar', (req, res) => {
  upload.single('avatar')(req, res, (err) => {
    if (err) {
      console.error('Multer upload error:', err)
      const status = err?.code === 'LIMIT_FILE_SIZE' ? 413 : 400
      return res.status(status).json({ error: err?.message || 'Upload failed' })
    }
    try {
      const fileName = req.file?.filename
      if (!fileName) {
        return res.status(400).json({ error: 'No file uploaded' })
      }
      const url = `/resources/avatars/${fileName}`
      return res.json({ url })
    } catch (e) {
      console.error('Upload error:', e)
      return res.status(500).json({ error: 'Upload failed' })
    }
  })
})

app.post('/api/upload-avatar-base64', async (req, res) => {
  try {
    const uid = String(req.body?.uid || 'user')
    const data = String(req.body?.data || '')
    const originalName = String(req.body?.filename || 'avatar.jpg')

    if (!data) return res.status(400).json({ error: 'No data provided' })

    const safeUid = uid.replace(/[^a-zA-Z0-9_-]/g, '') || 'user'
    const ext = (path.extname(originalName || '') || '.jpg').toLowerCase() || '.jpg'
    const base64 = data.includes(',') ? data.split(',')[1] : data
    const buffer = Buffer.from(base64, 'base64')

    const fileName = `${safeUid}_${Date.now()}${ext}`
    const filePath = path.join(avatarsDir, fileName)
    await fs.promises.writeFile(filePath, buffer)

    const url = `/resources/avatars/${fileName}`
    return res.json({ url })
  } catch (e) {
    console.error('Upload base64 error:', e)
    return res.status(500).json({ error: 'Upload failed' })
  }
})

app.listen(PORT, () => {
  console.log(`Avatar upload server listening on http://localhost:${PORT}`)
})