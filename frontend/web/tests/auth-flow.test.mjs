import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'

const __dirname = dirname(fileURLToPath(import.meta.url))
const root = resolve(__dirname, '..')

const readSource = (relativePath) => {
  return readFileSync(resolve(root, relativePath), 'utf8')
}

const tests = []

const test = (name, fn) => {
  tests.push({ name, fn })
}

test('route guard restores access token before redirecting protected routes', () => {
  const routerSource = readSource('src/router/index.js')

  assert.match(routerSource, /to\.meta\.requiresAuth && !userStore\.accessToken/)
  assert.match(routerSource, /await userStore\.restoreAccessToken\(\)/)
  assert.match(routerSource, /const token = userStore\.accessToken/)
})

test('request client refreshes once on 401 and retries with the new access token', () => {
  const apiSource = readSource('src/api/api.js')

  assert.match(apiSource, /const status = error\.response\?\.status/)
  assert.match(apiSource, /status === 401/)
  assert.match(apiSource, /originalRequest\._retry = true/)
  assert.match(apiSource, /const nextToken = await refreshAccessToken\(\)/)
  assert.match(apiSource, /originalRequest\.headers\.Authorization = `Bearer \$\{nextToken\}`/)
  assert.match(apiSource, /return api\(originalRequest\)/)
})

test('logout and refresh failure clear browser auth state without token storage writes', () => {
  const storeSource = readSource('src/stores/user.js')
  const qqCallbackSource = readSource('src/views/auth/QQCallbackView.vue')

  assert.match(storeSource, /function clearAuthState\(\)/)
  assert.match(storeSource, /accessToken\.value = ''/)
  assert.match(storeSource, /refreshToken\.value = ''/)
  assert.match(storeSource, /localStorage\.removeItem\('access_token'\)/)
  assert.match(storeSource, /localStorage\.removeItem\('refresh_token'\)/)
  assert.match(storeSource, /finally\s*\{\s*clearAuthState\(\)\s*\}/)

  assert.doesNotMatch(storeSource, /localStorage\.setItem\(['"]access_token['"]/)
  assert.doesNotMatch(storeSource, /localStorage\.setItem\(['"]refresh_token['"]/)
  assert.doesNotMatch(qqCallbackSource, /localStorage\.setItem\(['"]access_token['"]/)
  assert.doesNotMatch(qqCallbackSource, /localStorage\.setItem\(['"]refresh_token['"]/)
})

let failures = 0

for (const { name, fn } of tests) {
  try {
    fn()
    console.log(`ok - ${name}`)
  } catch (error) {
    failures += 1
    console.error(`not ok - ${name}`)
    console.error(error)
  }
}

if (failures > 0) {
  process.exitCode = 1
}
