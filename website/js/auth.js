/**
 * Masii Authentication with Supabase
 */

const SUPABASE_URL = 'https://herqdldjaxmfusjjpwdg.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhlcnFkbGRqYXhtZnVzampwd2RnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA3MzQ3NzcsImV4cCI6MjA4NjMxMDc3N30.IJF22gilascdOyI4gRFZMyI5PJjwuHAODSlcHxsZ7g4';

// Initialize Supabase client
const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

/**
 * Sign up with email
 */
async function signUp(email, password) {
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
    options: {
      emailRedirectTo: `${window.location.origin}/onboarding.html`
    }
  });

  if (error) {
    throw new Error(error.message);
  }

  return data;
}

/**
 * Sign in with email
 */
async function signIn(email, password) {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password
  });

  if (error) {
    throw new Error(error.message);
  }

  return data;
}

/**
 * Sign out
 */
async function signOut() {
  const { error } = await supabase.auth.signOut();
  if (error) {
    throw new Error(error.message);
  }
  window.location.href = '/';
}

/**
 * Get current session
 */
async function getSession() {
  const { data: { session }, error } = await supabase.auth.getSession();
  if (error) {
    console.error('Session error:', error);
    return null;
  }
  return session;
}

/**
 * Check if user is authenticated
 */
async function isAuthenticated() {
  const session = await getSession();
  return !!session;
}

/**
 * Get current user
 */
async function getUser() {
  const { data: { user }, error } = await supabase.auth.getUser();
  if (error) {
    console.error('User error:', error);
    return null;
  }
  return user;
}

/**
 * Require authentication (redirect if not logged in)
 */
async function requireAuth() {
  const authed = await isAuthenticated();
  if (!authed) {
    window.location.href = '/login.html';
  }
}

/**
 * Handle auth state changes
 */
supabase.auth.onAuthStateChange((event, session) => {
  console.log('Auth state changed:', event, session);
  
  if (event === 'SIGNED_IN') {
    // User just signed in
    console.log('User signed in:', session.user.email);
  } else if (event === 'SIGNED_OUT') {
    // User signed out
    console.log('User signed out');
  }
});
