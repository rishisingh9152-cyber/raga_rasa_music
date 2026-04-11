// Generate and persist user_id in localStorage
// Used for all API calls requiring user_id

export function getUserId(): string {
  const key = "raga_rasa_user_id";

  // Check if user_id already exists in localStorage
  let userId = localStorage.getItem(key);

  if (!userId) {
    // Generate new UUID v4
    userId = crypto.randomUUID();
    localStorage.setItem(key, userId);
  }

  return userId;
}
