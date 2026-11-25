(() => {
  const native = window.Capacitor?.isNativePlatform?.() === true;
  if (!native) return;

  const storageKey = 'chimbasmart.apiBaseUrl';
  const settings = document.querySelector('#nativeApiSettings');
  const input = document.querySelector('#nativeApiUrl');
  const saveButton = document.querySelector('#saveNativeApiUrl');
  const message = document.querySelector('#nativeApiMessage');
  const loginButton = document.querySelector('#go');
  const loginMessage = document.querySelector('#lm');

  settings.hidden = false;
  input.value = localStorage.getItem(storageKey) || '';
  loginButton.disabled = !input.value;

  function normalizeApiBase(value) {
    let url;
    try {
      url = new URL(value.trim());
    } catch {
      throw new Error('Weka anwani kamili ya seva, kwa mfano https://chimba.example.org.');
    }

    const localHost = ['localhost', '127.0.0.1', '[::1]'].includes(url.hostname);
    if ((url.protocol !== 'https:' && !(url.protocol === 'http:' && localHost))
        || url.username || url.password || url.search || url.hash) {
      throw new Error('Tumia HTTPS; HTTP inaruhusiwa kwa localhost ya majaribio pekee.');
    }
    return url.href.replace(/\/+$/, '');
  }

  function apiBase() {
    return localStorage.getItem(storageKey) || '';
  }

  saveButton.addEventListener('click', () => {
    try {
      const base = normalizeApiBase(input.value);
      localStorage.setItem(storageKey, base);
      input.value = base;
      loginButton.disabled = false;
      message.textContent = 'Anwani imehifadhiwa kwenye kifaa.';
    } catch (error) {
      loginButton.disabled = !apiBase();
      message.textContent = error.message;
    }
  });

  loginButton.addEventListener('click', event => {
    if (apiBase()) return;
    event.stopImmediatePropagation();
    loginMessage.textContent = 'Hifadhi anwani ya HTTPS ya seva kabla ya kuingia.';
  }, true);

  const nativeFetch = window.fetch.bind(window);
  window.fetch = (input, init) => {
    const base = apiBase();
    if (base && typeof input === 'string' && input.startsWith('/') && !input.startsWith('//')) {
      input = `${base}${input}`;
    }
    return nativeFetch(input, init);
  };
})();
