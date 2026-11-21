import { APIRequestContext, expect, Page } from "@playwright/test";

const API_URL = process.env.VITE_API_URL ?? "http://127.0.0.1:3000/api";

export interface TestUser {
  fullName: string;
  email: string;
  password: string;
  userId: string;
  token: string;
}

export function uniqueUser(): Pick<TestUser, "fullName" | "email" | "password"> {
  const suffix = `${Date.now()}${Math.random().toString(36).slice(2, 8)}`;
  return {
    fullName: `Test User ${suffix}`,
    email: `test.${suffix}@example.com`,
    password: "Password123!",
  };
}

export async function registerViaApi(
  request: APIRequestContext,
  user: Pick<TestUser, "fullName" | "email" | "password">,
): Promise<void> {
  const response = await request.post(`${API_URL}/users/register`, { data: user });
  expect(response.ok(), await response.text()).toBeTruthy();
}

export async function loginViaApi(
  request: APIRequestContext,
  user: Pick<TestUser, "email" | "password">,
): Promise<Pick<TestUser, "userId" | "token">> {
  const response = await request.post(`${API_URL}/users/login`, { data: user });
  expect(response.ok(), await response.text()).toBeTruthy();
  const body = (await response.json()) as { token: string; userId: string };
  return { token: body.token, userId: body.userId };
}

export async function createAuthenticatedUser(request: APIRequestContext): Promise<TestUser> {
  const user = uniqueUser();
  await registerViaApi(request, user);
  const { token, userId } = await loginViaApi(request, user);
  return { ...user, token, userId };
}

export async function authenticate(page: Page, user: Pick<TestUser, "token" | "userId">): Promise<void> {
  await page.addInitScript((session) => {
    localStorage.setItem("token", session.token);
    localStorage.setItem("userId", session.userId);
  }, { token: user.token, userId: user.userId });
}
