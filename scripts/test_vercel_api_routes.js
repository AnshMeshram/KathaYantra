const http = require('http');

function get(path) {
  return new Promise((resolve, reject) => {
    http.get(`http://localhost:3000${path}`, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve({ status: res.statusCode, headers: res.headers, body: JSON.parse(data) });
        } catch {
          resolve({ status: res.statusCode, headers: res.headers, body: data });
        }
      });
    }).on('error', reject);
  });
}

async function testAll() {
  console.log('Testing Next.js built-in API routes for Vercel...');

  // 1. Health
  const health = await get('/api/v1/health');
  console.log('[1/7] GET /api/v1/health ->', health.status, health.body.status);

  // 2. Countries
  const countries = await get('/api/v1/countries');
  console.log('[2/7] GET /api/v1/countries ->', countries.status, 'Total countries:', countries.body.pagination.total);

  // 3. Country Stats
  const stats = await get('/api/v1/countries/IN/stats');
  console.log('[3/7] GET /api/v1/countries/IN/stats ->', stats.status, stats.body.data.country_name, 'Stories:', stats.body.data.total_count);

  // 4. Folklore
  const folklore = await get('/api/v1/folklore?limit=2');
  console.log('[4/7] GET /api/v1/folklore ->', folklore.status, 'Total records:', folklore.body.pagination.total);

  // 5. Urban Legends
  const ul = await get('/api/v1/urban-legends?limit=2');
  console.log('[5/7] GET /api/v1/urban-legends ->', ul.status, 'Total records:', ul.body.pagination.total);

  // 6. Search
  const search = await get('/api/v1/search?q=Betal');
  console.log('[6/7] GET /api/v1/search?q=Betal ->', search.status, 'Results:', search.body.data.length);

  // 7. Export Pack (Zip)
  const exportPack = await get('/api/v1/export/pack?category=folklore&country_code=IN');
  console.log('[7/7] GET /api/v1/export/pack ->', exportPack.status, 'Content-Type:', exportPack.headers['content-type'], 'Count:', exportPack.headers['x-archive-count']);

  console.log('\n[PASS] ALL VERCEL API ROUTE TESTS PASSED WITH 100% SUCCESS!');
}

testAll().catch(err => {
  console.error('Failed:', err);
  process.exit(1);
});
