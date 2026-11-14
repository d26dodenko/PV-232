import { mkdirSync } from 'node:fs';
import { createApp } from './app.js';
import { createShop } from './shop.js';

mkdirSync('back/data', { recursive: true });
const shop = createShop(process.env.DB_PATH ?? 'back/data/shop.sqlite');
const server = createApp(shop).listen(Number(process.env.PORT ?? 3001), '127.0.0.1', (error) => {
  if (error) {
    console.error(error.message);
    shop.close();
    process.exitCode = 1;
    return;
  }
  console.log('API: http://127.0.0.1:' + server.address().port);
});
for (const signal of ['SIGTERM', 'SIGINT']) {
  process.on(signal, () => server.close(() => {
    shop.close();
    process.exit(0);
  }));
}
