import * as Sentry from '@sentry/react';
import axios from './axios';

let sentryInitialized = false;

/**
 * Initialize Sentry SDK with configuration from backend
 */
export async function initializeSentry() {
  if (sentryInitialized) {
    console.log('Sentry already initialized');
    return;
  }

  try {
    // Fetch Sentry configuration from backend
    const response = await axios.get('/api/v1/sentry-config/admin-frontend');
    const config = response.data;

    // Check if admin frontend Sentry is enabled
    if (!config || !config.dsn) {
      console.log('Sentry disabled or no DSN configured');
      return;
    }

    // Initialize Sentry
    Sentry.init({
      dsn: config.dsn,
      environment: config.environment || 'production',
      release: config.release_version || undefined,
      tracesSampleRate: parseFloat(config.traces_sample_rate) || 1.0,
      replaysSessionSampleRate: parseFloat(config.replays_session_sample_rate) || 0.1,
      replaysOnErrorSampleRate: parseFloat(config.replays_on_error_sample_rate) || 1.0,
      debug: config.debug_mode || false,

      integrations: [
        Sentry.browserTracingIntegration(),
        Sentry.replayIntegration({
          maskAllText: false,
          blockAllMedia: false,
        }),
      ],

      // Performance Monitoring
      tracePropagationTargets: ['localhost', /^\//],

      // Error filtering
      ignoreErrors: config.ignore_errors ? JSON.parse(config.ignore_errors) : [
        // Browser extensions
        'top.GLOBALS',
        // Random plugins/extensions
        'originalCreateNotification',
        'canvas.contentDocument',
        'MyApp_RemoveAllHighlights',
        // Facebook borked
        'fb_xd_fragment',
        // ISP "optimizing" proxy - `Cache-Control: no-transform` seems to reduce this. (thanks @acdha)
        // See http://stackoverflow.com/questions/4113268
        'bmi_SafeAddOnload',
        'EBCallBackMessageReceived',
        // See http://toolbar.conduit.com/Deblocker/TB-1220081.html
        'conduitPage',
      ],

      allowUrls: config.allowed_urls ? JSON.parse(config.allowed_urls) : undefined,
      denyUrls: config.denied_urls ? JSON.parse(config.denied_urls) : undefined,

      // Attach stack traces
      attachStacktrace: config.attach_stacktrace !== false,

      // Callbacks
      beforeSend(event, hint) {
        // Filter out certain errors or modify events here if needed
        const error = hint.originalException;

        // Don't send network errors for local development
        if (window.location.hostname === 'localhost' && error &&
            (error as any).message?.includes('Network')) {
          return null;
        }

        return event;
      },
    });

    sentryInitialized = true;
    console.log('Sentry initialized successfully');
  } catch (error) {
    console.error('Failed to initialize Sentry:', error);
    // Don't throw - app should work even if Sentry fails
  }
}

/**
 * Manually capture an exception
 */
export function captureException(error: Error, context?: Record<string, any>) {
  if (!sentryInitialized) {
    console.error('Sentry not initialized, logging error:', error);
    return;
  }

  if (context) {
    Sentry.withScope((scope) => {
      Object.entries(context).forEach(([key, value]) => {
        scope.setContext(key, value);
      });
      Sentry.captureException(error);
    });
  } else {
    Sentry.captureException(error);
  }
}

/**
 * Capture a message
 */
export function captureMessage(message: string, level: Sentry.SeverityLevel = 'info') {
  if (!sentryInitialized) {
    console.log('Sentry not initialized, logging message:', message);
    return;
  }

  Sentry.captureMessage(message, level);
}

/**
 * Set user context
 */
export function setUserContext(user: { id?: string; email?: string; username?: string }) {
  if (!sentryInitialized) return;

  Sentry.setUser(user);
}

/**
 * Clear user context (on logout)
 */
export function clearUserContext() {
  if (!sentryInitialized) return;

  Sentry.setUser(null);
}

/**
 * Add breadcrumb for debugging
 */
export function addBreadcrumb(breadcrumb: {
  message: string;
  category?: string;
  level?: Sentry.SeverityLevel;
  data?: Record<string, any>;
}) {
  if (!sentryInitialized) return;

  Sentry.addBreadcrumb(breadcrumb);
}
