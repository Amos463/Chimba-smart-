const crypto = require('node:crypto');
const { test, expect } = require('@playwright/test');

const baseURL = process.env.PWA_BASE_URL || 'http://127.0.0.1:8000';
const username = process.env.E2E_USER || 'juma';
const password = process.env.E2E_PASSWORD;
const jwtSecret = process.env.JWT_SECRET;
const png = Buffer.from(
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=',
  'base64',
);

test.setTimeout(240_000);

async function login(page) {
  await page.goto(baseURL);
  await page.locator('#ph').fill(username);
  await page.locator('#pin').fill(password);
  await page.locator('#go').click();
  await expect(page.locator('#home')).toHaveClass(/on/);
  await expect(page.locator('#projectSelect')).not.toBeEmpty();
}

async function capture(page, id, index, assay = '') {
  await goHome(page);
  await page.locator('[data-go="add"]').click();
  await page.context().setGeolocation({
    latitude: -3.1 + index * 0.001,
    longitude: 32.1 + index * 0.001,
    accuracy: 4,
  });
  await page.locator('#gps').click();
  await expect(page.locator('#gp')).toContainText('Mahali pamechukuliwa');
  await page.locator('#id').fill(id);
  if (assay) await page.locator('#gr').fill(assay);
  if (id === 'PWA-02') {
    await page.locator('#phfile').setInputFiles({
      name: 'field.png',
      mimeType: 'image/png',
      buffer: png,
    });
  }
  await page.locator('#sv').click();
  await expect(page.locator('#gp')).toContainText('Imehifadhiwa kwenye simu');
}

async function goHome(page) {
  while (await page.locator('#back').isVisible()) await page.locator('#back').click();
}

async function addLaterAssay(page, id, value) {
  await goHome(page);
  await page.locator('#home [data-go="mysamples"]').click();
  await page.locator(`[data-sample="${id}"]`).click();
  await page.locator('#assayValue').fill(String(value));
  await page.locator('#assayLab').fill('Pilot lab');
  await page.locator('#assayCertificate').fill(`CERT-${id}`);
  await page.locator('#assayMethod').fill('Fire assay');
  await page.locator('#assayBatch').fill('PILOT-1');
  await page.locator('#saveAssay').click();
}

async function serverSamples(page) {
  return page.evaluate(async () => {
    const projectId = localStorage.getItem('pid');
    const token = localStorage.getItem('tok');
    const response = await fetch(`/projects/${projectId}/samples`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!response.ok) return [];
    return (await response.json()).samples;
  });
}

function expiredToken(token) {
  const [header, payload] = token.split('.');
  const claims = JSON.parse(Buffer.from(payload, 'base64url').toString('utf8'));
  claims.exp = Math.floor(Date.now() / 1000) - 60;
  const encoded = Buffer.from(JSON.stringify(claims)).toString('base64url');
  const signingInput = `${header}.${encoded}`;
  const signature = crypto.createHmac('sha256', jwtSecret).update(signingInput).digest('base64url');
  return `${signingInput}.${signature}`;
}

test('PWA field capture, offline recovery, QA, jobs, refresh, conflicts and second device', async ({ browser }) => {
  const context = await browser.newContext({
    geolocation: { latitude: -3.1, longitude: 32.1, accuracy: 4 },
    permissions: ['geolocation'],
  });
  const page = await context.newPage();
  await login(page);
  await page.evaluate(() => navigator.serviceWorker.ready);

  await capture(page, 'PWA-BASE', 0, '1.0');
  await expect(page.locator('#qn')).toContainText('Data zimesawazishwa', { timeout: 20_000 });

  await context.setOffline(true);
  await capture(page, 'PWA-02', 1);
  await capture(page, 'PWA-03', 2);
  await page.reload();
  await expect(page.locator('#home')).toHaveClass(/on/);
  await page.locator('#home [data-go="mysamples"]').click();
  await expect(page.locator('[data-sample="PWA-02"]')).toBeVisible();
  await expect(page.locator('[data-sample="PWA-03"]')).toBeVisible();

  await context.setOffline(false);
  await page.locator('#retrySync').click();
  await expect.poll(async () => (await serverSamples(page)).some(sample => sample.sample_id === 'PWA-03'), { timeout: 30_000 }).toBe(true);
  await addLaterAssay(page, 'PWA-02', 2.0);
  await addLaterAssay(page, 'PWA-03', 3.0);

  await goHome(page);
  await capture(page, 'PWA-BDL', 3);
  await goHome(page);
  await page.locator('#home [data-go="mysamples"]').click();
  await page.locator('[data-sample="PWA-BDL"]').click();
  await page.locator('#assayValue').fill('0.01');
  await page.locator('#belowDetection').check();
  await page.locator('#detectionLimit').fill('0.02');
  await page.locator('#assayBatch').fill('PILOT-1');
  await page.locator('#saveAssay').click();
  await expect(page.locator('#sampleInfo')).toContainText('0.01 g/t');

  const sampleState = await serverSamples(page);
  const photoSample = sampleState.find(sample => sample.sample_id === 'PWA-02');
  expect(photoSample.attachment_count).toBe(1);
  expect(sampleState.find(sample => sample.sample_id === 'PWA-BDL').grade_basis).toBe('below_detection_half_dl');

  await goHome(page);
  await page.locator('[data-go="map"]').click();
  await expect(page.locator('#map')).toContainText('PWA-BASE');
  await goHome(page);
  await page.locator('[data-go="analysis"]').click();
  await page.locator('#jobEngine').selectOption('idw');
  await page.locator('#jobSampleType').selectOption('rock_chip');
  await page.locator('#runAnalysis').click();
  await expect(page.locator('#analysisResult')).toContainText('imekamilika', { timeout: 120_000 });
  await expect(page.locator('#jobGrid')).toBeVisible();

  await goHome(page);
  await page.locator('[data-go="rep"]').click();
  const downloadWait = page.waitForEvent('download');
  await page.locator('#pdf').click();
  const download = await downloadWait;
  expect(download.suggestedFilename()).toBe('ripoti.pdf');

  const originalToken = await page.evaluate(() => localStorage.getItem('tok'));
  const expired = expiredToken(originalToken);
  await page.evaluate(token => localStorage.setItem('tok', token), expired);
  await goHome(page);
  await page.locator('#home [data-go="mysamples"]').click();
  await page.locator('#refreshSamples').click();
  await expect.poll(() => page.evaluate(() => localStorage.getItem('tok'))).not.toBe(expired);

  const secondContext = await browser.newContext();
  const secondPage = await secondContext.newPage();
  await login(secondPage);
  await secondPage.locator('#home [data-go="mysamples"]').click();
  await expect(secondPage.locator('[data-sample="PWA-03"]')).toBeVisible({ timeout: 30_000 });

  const conflict = await secondPage.evaluate(async () => {
    const token = localStorage.getItem('tok');
    const projectId = localStorage.getItem('pid');
    const headers = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' };
    const pulled = await fetch(`/sync/pull?project_id=${projectId}&cursor=0&limit=200`, { headers });
    const records = (await pulled.json()).records;
    const sample = records.find(record => record.record_type === 'sample' && record.payload.sample_id === 'PWA-BASE');
    const response = await fetch('/sync/push', {
      method: 'POST',
      headers,
      body: JSON.stringify({ records: [{
        record_uuid: sample.record_uuid,
        project_id: projectId,
        record_type: sample.record_type,
        payload: { ...sample.payload, description: 'conflicting field edit' },
        created_at_utc: sample.created_at_utc,
        updated_at_utc: new Date().toISOString(),
        device_id: 'pwa-e2e-second-device',
        source_method: 'pwa-e2e',
        crs: 'EPSG:4326',
      }] }),
    });
    return (await response.json()).accepted[0];
  });
  expect(conflict.status).toBe('conflict');
  await goHome(secondPage);
  await secondPage.locator('#retrySync').click();
  await expect(secondPage.locator('#conflictList .conflict-card')).toBeVisible();
  await secondPage.getByRole('button', { name: 'Hifadhi la seva' }).click();
  await expect(secondPage.locator('#conflictList .conflict-card')).toHaveCount(0);

  await secondContext.close();
  await context.close();
});
