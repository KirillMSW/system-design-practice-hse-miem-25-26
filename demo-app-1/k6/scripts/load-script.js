import http from 'k6/http';
import { check, sleep, group } from 'k6';

function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function pickUserIdSkewed() {
  return Math.random() < 0.7 ? 1 : 2;
}

function createOrder({ skewUsers = false } = {}) {
  const payload = JSON.stringify({
    user_id: skewUsers ? pickUserIdSkewed() : randomInt(1, 2),
    amount: Math.random() * 100,
    description: 'k6 load',
  });

  const res = http.post('http://localhost:8081/api/orders', payload, {
    headers: { 'Content-Type': 'application/json' },
    tags: { endpoint: 'POST /api/orders' },
  });

  check(res, { created: (r) => r.status === 200 || r.status === 201 });
  return res;
}

function listOrders() {
  const res = http.get('http://localhost:8080/api/orders', {
    tags: { endpoint: 'GET /api/orders' },
  });

  check(res, { list_ok: (r) => r.status === 200 });
  return res;
}

export function mixedTraffic() {
  if (Math.random() < 0.8) createOrder();
  else listOrders();
  sleep(0.05);
}

export function customTraffic() {
  group('custom', () => {
    if (Math.random() < 0.85) {
      createOrder({ skewUsers: true });
      if (Math.random() < 0.6) listOrders();
    } else {
      listOrders();
    }
  });

  sleep(Math.random() * 0.3);
}

export const options = {
  scenarios: {
    storm: {
      executor: 'ramping-vus',
      exec: 'mixedTraffic',
      startTime: '0s',
      startVUs: 0,
      stages: [
        { duration: '10s', target: 1000 },
        { duration: '1m40s', target: 1000 },
        { duration: '10s', target: 0 },
      ],
      gracefulRampDown: '10s',
    },
    wave: {
      executor: 'ramping-vus',
      exec: 'mixedTraffic',
      startTime: '2m',
      startVUs: 0,
      stages: [{ duration: '2m', target: 500 }],
      gracefulRampDown: '10s',
    },
    custom: {
      executor: 'ramping-vus',
      exec: 'customTraffic',
      startTime: '4m',
      startVUs: 0,
      stages: [
        { duration: '30s', target: 300 },
        { duration: '30s', target: 50 },
        { duration: '30s', target: 300 },
        { duration: '30s', target: 0 },
      ],
      gracefulRampDown: '10s',
    },
  },
};

export default mixedTraffic;
