/**
 * Masii Authentication with Supabase
 */

const SUPABASE_URL = 'https://herqdldjaxmfusjjpwdg.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhlcnFkbGRqYXhtZnVzampwd2RnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA3MzQ3NzcsImV4cCI6MjA4NjMxMDc3N30.IJF22gilascdOyI4gRFZMyI5PJjwuHAODSlcHxsZ7g4';

// Initialize Supabase client (wait for window.supabase to be available)
let supabase;
if (window.supabase) {
  supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
} else {
  console.error('Supabase library not loaded');
}

/**
 * Sign up with email
 */
window.signUp = async function(email, password) {
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
window.signIn = async function(email, password) {
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
window.signOut = async function() {
  const { error } = await supabase.auth.signOut();
  if (error) {
    throw new Error(error.message);
  }
  window.location.href = '/';
}

/**
 * Get current session
 */
window.getSession = async function() {
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
window.isAuthenticated = async function() {
  const session = await getSession();
  return !!session;
}

/**
 * Get current user
 */
window.getUser = async function() {
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
window.requireAuth = async function() {
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
