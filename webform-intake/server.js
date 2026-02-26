const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = Number(process.env.PORT || 4173);
const PUBLIC_DIR = path.join(__dirname, 'public');
const DATA_DIR = path.join(__dirname, 'data');
const SUBMISSIONS_FILE = path.join(DATA_DIR, 'submissions.ndjson');

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.txt': 'text/plain; charset=utf-8'
};

function send(res, status, body, contentType = 'text/plain; charset=utf-8') {
  res.writeHead(status, {
    'Content-Type': contentType,
    'Cache-Control': 'no-store'
  });
  res.end(body);
}

function safePathFromUrl(urlPath) {
  const decoded = decodeURIComponent(urlPath.split('?')[0]);
  const normalized = path.normalize(decoded).replace(/^\/+/, '');
  return path.join(PUBLIC_DIR, normalized);
}

function serveFile(res, filePath) {
  fs.readFile(filePath, (err, content) => {
    if (err) {
      send(res, 404, 'Not found');
      return;
    }
    const ext = path.extname(filePath).toLowerCase();
    const contentType = MIME_TYPES[ext] || 'application/octet-stream';
    send(res, 200, content, contentType);
  });
}

function collectBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', (chunk) => {
      body += chunk;
      if (body.length > 1_000_000) {
        reject(new Error('Payload too large'));
      }
    });
    req.on('end', () => resolve(body));
    req.on('error', reject);
  });
}

async function handleApiIntake(req, res) {
  try {
    const raw = await collectBody(req);
    const payload = JSON.parse(raw || '{}');

    const record = {
      submitted_at: new Date().toISOString(),
      payload
    };

    if (!fs.existsSync(DATA_DIR)) {
      fs.mkdirSync(DATA_DIR, { recursive: true });
    }
    fs.appendFileSync(SUBMISSIONS_FILE, JSON.stringify(record) + '\n', 'utf-8');

    send(res, 200, JSON.stringify({ ok: true }), 'application/json; charset=utf-8');
  } catch (error) {
    send(res, 400, JSON.stringify({ ok: false, error: error.message }), 'application/json; charset=utf-8');
  }
}

const server = http.createServer(async (req, res) => {
  const method = req.method || 'GET';
  const urlPath = (req.url || '/').split('?')[0];

  if (method === 'POST' && urlPath === '/api/intake') {
    await handleApiIntake(req, res);
    return;
  }

  if (method !== 'GET') {
    send(res, 405, 'Method not allowed');
    return;
  }

  if (urlPath === '/') {
    serveFile(res, path.join(PUBLIC_DIR, 'index.html'));
    return;
  }

  if (urlPath === '/intake') {
    res.writeHead(302, { Location: '/intake/' });
    res.end();
    return;
  }

  const filePath = safePathFromUrl(urlPath);
  if (!filePath.startsWith(PUBLIC_DIR)) {
    send(res, 403, 'Forbidden');
    return;
  }

  if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
    serveFile(res, filePath);
    return;
  }

  if (fs.existsSync(filePath) && fs.statSync(filePath).isDirectory()) {
    const indexFile = path.join(filePath, 'index.html');
    if (fs.existsSync(indexFile)) {
      serveFile(res, indexFile);
      return;
    }
  }

  send(res, 404, 'Not found');
});

server.listen(PORT, () => {
  console.log(`Jodi local site running at http://localhost:${PORT}`);
  console.log(`Intake form: http://localhost:${PORT}/intake`);
});
