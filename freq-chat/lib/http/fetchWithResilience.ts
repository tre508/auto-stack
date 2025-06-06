export interface FetchOptions extends RequestInit {
  // Add any custom options here, e.g., for retries
  serviceName: string; // For logging purposes
}

export async function fetchWithResilience(
  url: string,
  options: FetchOptions,
): Promise<Response> {
  const { serviceName, ...fetchOptions } = options;

  if (!url) {
    console.error(`[${serviceName}] Error: URL is undefined.`);
    throw new Error(`[${serviceName}] URL is undefined.`);
  }

  console.log(`[${serviceName}] Making request to ${url} with options:`, fetchOptions);

  try {
    const response = await fetch(url, fetchOptions);

    if (!response.ok) {
      let errorBody = '';
      try {
        errorBody = await response.text();
      } catch (e) {
        // Ignore if reading body fails
      }
      console.warn(
        `[${serviceName}] Request to ${url} failed with status ${response.status}. Body: ${errorBody}`,
      );
      // You might want to throw a custom error here or handle specific status codes
    } else {
      console.log(`[${serviceName}] Request to ${url} successful with status ${response.status}.`);
    }
    return response;
  } catch (error: any) {
    console.error(
      `[${serviceName}] Network error or other issue making request to ${url}:`,
      error.message,
      error.stack,
    );
    throw error; // Re-throw the error to be handled by the caller
  }
}

// Example of how to add a simple retry mechanism (conceptual)
// This is a basic illustration and would need more robust implementation for production
export async function fetchWithRetries(
  url: string,
  options: FetchOptions & { retries?: number; delayMs?: number },
): Promise<Response> {
  const { retries = 3, delayMs = 1000, ...baseOptions } = options;
  let attempt = 0;
  while (attempt < retries) {
    try {
      const response = await fetchWithResilience(url, baseOptions);
      if (response.ok || (response.status >= 400 && response.status < 500 && response.status !== 429) ) { // Don't retry on client errors other than 429
        return response;
      }
      // Optionally, only retry on specific server errors or rate limits (e.g. 5xx, 429)
      if (response.status < 500 && response.status !== 429) {
          return response;
      }
      console.warn(`[${options.serviceName}] Retrying request to ${url} (attempt ${attempt + 1}/${retries}) after status ${response.status}`);

    } catch (error) {
      console.warn(`[${options.serviceName}] Retrying request to ${url} (attempt ${attempt + 1}/${retries}) after error: ${error}`);
      // If it's a network error, it will be caught here.
    }
    attempt++;
    if (attempt < retries) {
      await new Promise(resolve => setTimeout(resolve, delayMs * Math.pow(2, attempt -1))); // Exponential backoff
    }
  }
  console.error(`[${options.serviceName}] Request to ${url} failed after ${retries} retries.`);
  // Fallback to throwing an error or returning a specific error response
  throw new Error(`[${options.serviceName}] Request failed after ${retries} retries`);
} 