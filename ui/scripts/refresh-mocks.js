#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const {
  validateConfigMock,
  validatePermissionsMock,
  validateCallsMock,
} = require('../src/mocks/schemas');

const MOCKS = [
  { key: 'config', file: 'config.json', validator: validateConfigMock },
  { key: 'permissions', file: 'permissions.json', validator: validatePermissionsMock },
  { key: 'calls', file: 'llamadas.json', validator: validateCallsMock },
];

const mocksDir = path.resolve(__dirname, '../src/mocks');
const outputDir = path.resolve(__dirname, '../logs/mocks');

fs.mkdirSync(outputDir, { recursive: true });

const snapshot = {
  generatedAt: new Date().toISOString(),
  mocks: [],
};

for (const mock of MOCKS) {
  const rawPath = path.join(mocksDir, mock.file);
  const rawData = fs.readFileSync(rawPath, 'utf-8');
  const parsed = JSON.parse(rawData);
  mock.validator(parsed);

  snapshot.mocks.push({ key: mock.key, size: Buffer.byteLength(rawData), entries: Object.keys(parsed).length });
}

const snapshotPath = path.join(outputDir, `snapshot-${Date.now()}.json`);
fs.writeFileSync(snapshotPath, JSON.stringify(snapshot, null, 2));

console.log(`Mock snapshot generated at ${snapshotPath}`);
