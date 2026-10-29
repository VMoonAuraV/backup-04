/* GRE Context Lab local example provider interface v1.
 * This is a no-op contract only. Implement the ignored local file
 * docs/local-example-provider.local.js to connect your own local model.
 */
(function () {
  if (window.GREContextLabExampleProvider) return;
  window.GREContextLabExampleProvider = {
    apiVersion: 1,
    isConfigured: false,
    async generateExamples(request) {
      throw new Error("Local example provider is not configured. See docs/LOCAL_EXAMPLE_PROVIDER.md.");
    }
  };
})();
