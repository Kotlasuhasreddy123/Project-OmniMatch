import { browserCsp } from '../../security-policy';

test('production policy blocks plugins and external scripts while permitting the configured API', () => {
  const previousMode = process.env.NODE_ENV;
  const previousApi = process.env.NEXT_PUBLIC_API_URL;
  try {
    Object.assign(process.env, { NODE_ENV: 'production', NEXT_PUBLIC_API_URL: 'https://api.example.org/path?ignored=1' });
    const policy = browserCsp();
    expect(policy).toContain("object-src 'none'");
    expect(policy).toContain("base-uri 'self'");
    expect(policy).toContain("script-src 'self' 'unsafe-inline';");
    expect(policy).not.toContain('unsafe-eval');
    expect(policy).toContain('https://api.example.org');
    expect(policy).not.toContain('ignored=1');
  } finally {
    Object.assign(process.env, { NODE_ENV: previousMode });
    if (previousApi === undefined) delete process.env.NEXT_PUBLIC_API_URL;
    else process.env.NEXT_PUBLIC_API_URL = previousApi;
  }
});
