import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { copyFileSync } from 'fs'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    {
      name: 'copy-extension-files',
      closeBundle() {
        // Copy manifest.json to dist
        try {
          copyFileSync('manifest.json', 'dist/manifest.json')
          console.log('✓ Copied manifest.json to dist/')
        } catch (e) {
          console.log('⚠ manifest.json not found')
        }
        
        // Copy background.js to dist
        try {
          copyFileSync('background.js', 'dist/background.js')
          console.log('✓ Copied background.js to dist/')
        } catch (e) {
          console.log('⚠ background.js not found')
        }
      }
    }
  ],
  base: './',
  build: {
    rollupOptions: {
      output: {
        assetFileNames: 'assets/[name]-[hash][extname]',
        chunkFileNames: 'assets/[name]-[hash].js',
        entryFileNames: 'assets/[name]-[hash].js',
      },
    },
  },
})
